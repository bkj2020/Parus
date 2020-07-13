# *** Include Django belong classes ***
from django.shortcuts import render
from django.views.generic.list import View
from django.views.generic import ListView
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
import datetime
from .models import Country, Hot_guest, Hot_room, Hot_book

# *** Include Global python classes ***
import io
import json
import logging
from xlsxwriter.workbook import Workbook

# Create your views here.
# Create your views here.
class BasePage(View):
    template_name = 'index.html'

    def get(self, request):
        return render(request, 'index.html')


class Apartments(ListView):  # main page class
    model = Hot_book
    template_name = 'apartments.html'

    def get_context_data(self, *, object_list=None, **kwargs):  # this function for list of views not a single view

        context = super().get_context_data(**kwargs)  # for nasledovaniya from ListView class
        # Get list of room
        rst_Hot_rooms = Hot_room.objects.all().order_by('floor', 'orderby')

        # Divide rooms by floor
        floors = {}  # empty dict
        for room in rst_Hot_rooms:
            # if dict is empty we have definde first keys(or index) otherwise will have keyerror(or index error)
            if room.floor in floors.keys():
                floors[room.floor].append(room.roomnum)  # if dict is not empty it will work
            else:
                floors[room.floor] = [room.roomnum]

        # Get room properties
        room_prop = {}  # empty dict
        for room in rst_Hot_rooms:
            room_prop[room.roomnum] = room.roomtype
        # End - room properties

        # Get room status
        room_stat = {}  # empty dict
        for stat in rst_Hot_rooms:
            room_stat[stat.roomnum] = stat.status
        # End - Get room status

        # Get maximum number of room in floor
        room_num = max([len(fl) for fl in floors.values()])
        # or get it from list #num_room = len(list(floors))

        # Divide by row
        rooms = {}
        for row in range(room_num):
            for fl in floors.values():  # 501, 502] [607, 608, 609, 610] [701] [1515, 1516, 1517]
                room = fl[row] if row < len(fl) else 0
                if row in rooms.keys():
                    rooms[row].append(room)
                else:
                    rooms[row] = [room]

        # Query Set rom conditions
        queryset = Hot_room.objects.all()
        room_condition = [st.status for st in queryset]
        stat_rp = room_condition.count('repair')
        stat_fr = room_condition.count('free')
        stat_bz = room_condition.count('busy')
        stat_dr = room_condition.count('dirty')
        room_info = [stat_rp, stat_fr, stat_bz, stat_dr]

        context['floors'] = floors
        context['rooms'] = rooms
        context['room_prop'] = room_prop
        context['room_stat'] = room_stat
        context['room_info'] = room_info
        return context


class GestReportByReseption(Apartments, ListView):
    model = Hot_book
    template_name = 'gest_report.html'

    def post(self, request, *args, **kwargs):
        """ Return XLS file with report results"""
        # Get start data from POST request from gest_report.html
        start_date = request.POST.get("start")
        finish_date = request.POST.get("finish")

        # napisat funksiyu dlya proverki right date
        if start_date == '':
            start_date = datetime.datetime.now().strftime('%Y-%m-%d')

        if finish_date == '':
            finish_date = datetime.datetime.now().strftime('%Y-%m-%d')

        # Get data in cash and dump into xml file
        output = io.BytesIO()

        # Prepare data
        queryset = Hot_book.objects.all().values("arrdate", 'depdate', 'paymethod', 'currency', 'payrate', "fk_gid__surname", "fk_gid__name", "fk_gid__company",
                                                 "fk_gid__fk_cid__name", "fk_rid__roomnum", "fk_rid__roomtype")\
            .filter(active=True).filter(arrdate__gte=start_date, arrdate__lte=finish_date)\
            .order_by('fk_rid__roomnum')
            # filter beetwin -> .filter(active=True, arrdate__gte=start_date, arrdate__lte=finish_date)\

        # make the queryset iv list
        gest_reprt = [gest_info for gest_info in queryset]
        # End -> data

        # Prepare excel file and fill the data
        book = Workbook(output)
        sheet = book.add_worksheet('Отчет по проживающим')

        # Prepare format variables
        fmt_title = book.add_format({'valign': 'vcenter', 'font_size': 12, 'font_name': 'Arial', 'bold': 1, 'border': 1})
        fmt_column = book.add_format({'font_size': 12, 'font_name': 'Arial', 'bold': True, 'border': 1, 'text_wrap': 1, 'align': 'center', 'valign': 'vcenter'})
        fmt_cell = book.add_format({'align': 'center', 'font_size': 10, 'font_name': 'Arial', 'border': 1})
        fmt_total = book.add_format({'font_size': 10, 'font_name': 'Arial', 'border': 1, 'bold': True, 'align': 'center'})

        # Set title of report
        sheet.merge_range('A1:N1', 'FO Guest in house', fmt_title)
        sheet.merge_range('A2:N2', 'As per the', fmt_title)

        # Set column names
        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 6)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 6)
        sheet.set_column('E:E', 14)
        sheet.set_column('F:F', 25)
        sheet.set_column('G:G', 17)
        sheet.set_column('H:H', 22)
        sheet.set_column('I:I', 14)
        sheet.set_column('J:J', 10)
        sheet.set_column('K:K', 9)
        sheet.set_column('L:L', 9)
        sheet.set_column('M:M', 16)
        sheet.set_column('N:N', 19)
        sheet.set_column('O:O', 19)

        title_rep = {'A': 'Arrival Date', 'B': 'ETA', 'C': 'Departure Date', 'D': 'ETA','E': 'Room number', 'F': 'Guest Name'
            , 'G': 'Nationality', 'H': 'Company Name', 'I': 'Number of Pax', 'J': 'Room type', 'K': 'Rate USD', 'L': 'Rate DTM'
            , 'M': 'Payment method', 'N': 'Booking entered by',
                     }

        for key, value in title_rep.items():
            sheet.write(key + '3', value, fmt_total)

        # Set table data
        row = 3
        for records in gest_reprt:
            sheet.write(row, 0, records['arrdate'].strftime('%d.%m.%Y'), fmt_cell)  # arrdate
            sheet.write(row, 1, records['arrdate'].strftime('%H:%M'), fmt_cell)  # arrtime
            sheet.write(row, 2, records['depdate'].strftime('%d.%m.%Y'), fmt_cell)  # depdate
            sheet.write(row, 3, records['depdate'].strftime('%H:%M'), fmt_cell)  # deptime
            sheet.write(row, 4, records['fk_rid__roomnum'], fmt_cell)  # k_rid
            sheet.write(row, 5, records['fk_gid__surname'], fmt_cell)  # fk_gid
            sheet.write(row, 6, records['fk_gid__fk_cid__name'], fmt_cell)  # Country
            sheet.write(row, 7, records['fk_gid__company'], fmt_cell)  # Company Name
            sheet.write(row, 8, 'Number of Pax', fmt_cell)  # Number of Pax
            sheet.write(row, 9, records['fk_rid__roomtype'], fmt_cell)  # Room type
            sheet.write(row, 10, records['paymethod'], fmt_cell)  # rate usd
            sheet.write(row, 11, records['paymethod'], fmt_cell)  # rate dtm
            sheet.write(row, 12, records['payrate'], fmt_cell)  # pay metod
            sheet.write(row, 13, 'Booking entered by', fmt_cell)  # Booking entered by
            row += 1

        book.close()
        # End -> Prepare

        # Construct response
        output.seek(0)
        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename=guests_report.xlsx"
        response['Cache-Control'] = " max-age=0"
        # End -> Construct
        output.close()
        return response


class MigrateReportByReseption(ListView):
    model = Hot_book
    template_name = 'migration_report.html'

    def post(self, request, *args, **kwargs):
        """ Return XLS file with report results"""
        # Get start data from POST request from migration_report.html
        start_date = request.POST.get("start")
        finish_date = request.POST.get("finish")

    # napisat funksiyu dlya proverki right date

        # Get data in cash and dump into xml file
        output = io.BytesIO()

        # Prepare data
        queryset = Hot_book.objects.all().values("fk_gid__surname", "fk_gid__name", "fk_rid__roomnum", "fk_gid__birthdate", "fk_gid__gender",
             "fk_gid__fk_cid__name", "fk_gid__typeofvisa", "fk_gid__company", "arrdate", 'depdate')\
            .filter(active=True).filter(arrdate__gte=start_date, arrdate__lte=finish_date)\
            .order_by('fk_rid__roomnum')
            # filter beetwin -> .filter(active=True, arrdate__gte=start_date, arrdate__lte=finish_date)\

        # make the queryset iv list
        migrate_reprt = [migrate_info for migrate_info in queryset]
        # End -> data

        # Prepare excel file and fill the data
        book = Workbook(output)
        sheet = book.add_worksheet('Отчет в Миграционную службу')

        # Prepare format variables
        fmt_title = book.add_format({'valign': 'vcenter', 'align': 'center', 'font_size': 12, 'font_name': 'Times New Roman', 'border': 1, 'bold': 1})
        fmt_mgr_title = book.add_format({'align': 'center', 'font_size': 14, 'font_name': 'Times New Roman', 'border': 1, 'bold': 1})
        fmt_cell = book.add_format({'align': 'center', 'font_size': 10, 'font_name': 'Arial', 'border': 1})
        fmt_total = book.add_format({'font_size': 10, 'font_name': 'Arial', 'border': 1, 'bold': True, 'align': 'center'})

        # Set title of report
        sheet.merge_range('A1:J1', '"Yyldyz myhmanhanasynda ýaşaýan daşary ýurt raýatlary barada" Maglumat', fmt_mgr_title)

        # Set column names
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 14)
        sheet.set_column('D:D', 14)
        sheet.set_column('E:E', 8)
        sheet.set_column('F:F', 18)
        sheet.set_column('G:G', 17)
        sheet.set_column('H:H', 16)
        sheet.set_column('I:I', 24)
        sheet.set_column('J:J', 24)

        title_rep = {'A': '#', 'B': 'F.A.A', 'C': 'Otag Belgisi', 'D': 'Doglan Sene','E': 'Jynsy', 'F': 'Raýatlygy'
            , 'G': 'Wizanyň görnüşi', 'H': 'Çagyryjy tarap', 'I': 'Myhmanyň giren wagty', 'J': 'Myhmanyň cykan wagty',
                     }

        for key, value in title_rep.items():
            sheet.write(key + '2', value, fmt_title)

        sheet.set_row(1, 30)

        # Set table data
        count = 1
        row = 2
        for records in migrate_reprt:
            sheet.write(row, 0, count, fmt_cell)  # arrdate
            sheet.write(row, 1, records['fk_gid__surname'], fmt_cell)  # arrtime
            sheet.write(row, 2, records['fk_rid__roomnum'], fmt_cell)  # depdate
            sheet.write(row, 3, records['fk_gid__birthdate'], fmt_cell)  # fk_gid
            sheet.write(row, 4, records['fk_gid__gender'], fmt_cell)  # Country
            sheet.write(row, 5, records['fk_gid__fk_cid__name'], fmt_cell)  # deptime
            sheet.write(row, 6, records['fk_gid__typeofvisa'], fmt_cell)  # Room type
            sheet.write(row, 7, records['fk_gid__company'], fmt_cell)  # Company Name
            sheet.write(row, 8, records['arrdate'].strftime('%d.%m.%Y'), fmt_cell)  # arrdate
            sheet.write(row, 9, records['depdate'].strftime('%d.%m.%Y'), fmt_cell)  # depdate
            row += 1
            count += 1

        book.close()
        # End -> Prepare

        # Construct response
        output.seek(0)
        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename=guests_report.xlsx"
        response['Cache-Control'] = " max-age=0"
        # End -> Construct
        output.close()
        return response


class MigrateCompanyReportByReseption(ListView):
    model = Hot_book
    template_name = 'migrt_comp_rep.html'

    def get_context_data(self, *args, **kwargs):
        context = super(MigrateCompanyReportByReseption, self).get_context_data(*args, **kwargs)
        qstp = Hot_guest.objects.all().values('company').order_by('company').distinct()
        qst_comp = [i for i in qstp]
        context['queryset_comp'] = qst_comp
        return context

    def post(self, request, *args, **kwargs):
        """ Return XLS file with report results"""
        # Get start data from POST request from migration_report.html
        firma = request.POST.get("comp")
        start_date = request.POST.get("start")
        finish_date = request.POST.get("finish")


    # napisat funksiyu dlya proverki right date
        if start_date == '':
            start_date = datetime.datetime.now().strftime('%Y-%m-%d')

        if finish_date == '':
            finish_date = datetime.datetime.now().strftime('%Y-%m-%d')

        # Get data in cash and dump into xml file
        output = io.BytesIO()

        # Prepare data
        queryset = Hot_book.objects.all().values("fk_gid__surname", "fk_gid__name", "fk_rid__roomnum", "fk_gid__birthdate", "fk_gid__gender",
             "fk_gid__fk_cid__name", "fk_gid__typeofvisa", "fk_gid__company", "arrdate", 'depdate')\
            .filter(active=True).filter(arrdate__gte=start_date, arrdate__lte=finish_date).filter(fk_gid__company__startswith=firma)\
            .order_by('fk_gid__company')
            # filter beetwin -> .filter(active=True, arrdate__gte=start_date, arrdate__lte=finish_date)\

        # make the queryset iv list
        migrate_reprt = [migrate_info for migrate_info in queryset]
        # End -> data

        # Prepare excel file and fill the data
        book = Workbook(output)
        sheet = book.add_worksheet('Отчет по компаниям')

        # Prepare format variables
        fmt_title = book.add_format({'valign': 'vcenter', 'align': 'center', 'font_size': 12, 'font_name': 'Times New Roman', 'border': 1, 'bold': 1})
        fmt_mgr_title = book.add_format({'align': 'center', 'font_size': 14, 'font_name': 'Times New Roman', 'border': 1, 'bold': 1})
        fmt_cell = book.add_format({'align': 'center', 'font_size': 10, 'font_name': 'Arial', 'border': 1})
        fmt_total = book.add_format({'font_size': 10, 'font_name': 'Arial', 'border': 1, 'bold': True, 'align': 'center'})

        # Set title of report
        sheet.merge_range('A1:J1', '"Yyldyz myhmanhanasynda ýaşaýan daşary ýurt raýatlary barada" Maglumat', fmt_mgr_title)

        # Set column names
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 14)
        sheet.set_column('D:D', 14)
        sheet.set_column('E:E', 8)
        sheet.set_column('F:F', 18)
        sheet.set_column('G:G', 17)
        sheet.set_column('H:H', 16)
        sheet.set_column('I:I', 24)
        sheet.set_column('J:J', 24)

        title_rep = {'A': '#', 'B': 'F.A.A', 'C': 'Otag Belgisi', 'D': 'Doglan Sene','E': 'Jynsy', 'F': 'Raýatlygy'
            , 'G': 'Wizanyň görnüşi', 'H': 'Çagyryjy tarap', 'I': 'Myhmanyň giren wagty', 'J': 'Myhmanyň cykan wagty',
                     }

        for key, value in title_rep.items():
            sheet.write(key + '2', value, fmt_title)

        sheet.set_row(1, 30)

        # Set table data
        count = 1
        row = 2
        for records in migrate_reprt:
            sheet.write(row, 0, count, fmt_cell)  # arrdate
            sheet.write(row, 1, records['fk_gid__surname'], fmt_cell)  # arrtime
            sheet.write(row, 2, records['fk_rid__roomnum'], fmt_cell)  # depdate
            sheet.write(row, 3, records['fk_gid__birthdate'], fmt_cell)  # fk_gid
            sheet.write(row, 4, records['fk_gid__gender'], fmt_cell)  # Country
            sheet.write(row, 5, records['fk_gid__fk_cid__name'], fmt_cell)  # deptime
            sheet.write(row, 6, records['fk_gid__typeofvisa'], fmt_cell)  # Room type
            sheet.write(row, 7, records['fk_gid__company'], fmt_cell)  # Company Name
            sheet.write(row, 8, records['arrdate'].strftime('%d.%m.%Y'), fmt_cell)  # arrdate
            sheet.write(row, 9, records['depdate'].strftime('%d.%m.%Y'), fmt_cell)  # depdate
            row += 1
            count += 1

        book.close()
        # End -> Prepare

        # Construct response
        output.seek(0)
        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename=guests_report.xlsx"
        response['Cache-Control'] = " max-age=0"
        # End -> Construct
        return response


class MigrateCountryReportByReseption(ListView):
    model = Hot_book
    template_name = 'migrt_country_rep.html'

    def get_context_data(self, *args, **kwargs):
        context = super(MigrateCountryReportByReseption, self).get_context_data(*args, **kwargs)
        qstp = Hot_guest.objects.all().values('fk_cid__name').order_by('fk_cid__name').distinct()
        qst_counrty = [i for i in qstp]
        context['queryset_counrty'] = qst_counrty
        return context

    def post(self, request, *args, **kwargs):
        """ Return XLS file with report results"""
        # Get start data from POST request from migration_report.html
        strana = request.POST.get("dovlet")
        start_date = request.POST.get("start")
        finish_date = request.POST.get("finish")


    # napisat funksiyu dlya proverki right date
        if start_date == '':
            start_date = datetime.datetime.now().strftime('%Y-%m-%d')

        if finish_date == '':
            finish_date = datetime.datetime.now().strftime('%Y-%m-%d')

        # Get data in cash and dump into xml file
        output = io.BytesIO()

        # Prepare data
        queryset = Hot_book.objects.all().values("fk_gid__surname", "fk_gid__name", "fk_rid__roomnum", "fk_gid__birthdate", "fk_gid__gender",
             "fk_gid__fk_cid__name", "fk_gid__typeofvisa", "fk_gid__company", "arrdate", 'depdate')\
            .filter(active=True).filter(arrdate__gte=start_date, arrdate__lte=finish_date).filter(fk_gid__fk_cid__name=strana)\
            .order_by('fk_gid__fk_cid__name')
            # filter beetwin -> .filter(active=True, arrdate__gte=start_date, arrdate__lte=finish_date)\

        # make the queryset iv list
        migrate_reprt = [migrate_info for migrate_info in queryset]
        # End -> data

        # Prepare excel file and fill the data
        book = Workbook(output)
        sheet = book.add_worksheet('Отчет по странам')

        # Prepare format variables
        fmt_title = book.add_format({'valign': 'vcenter', 'align': 'center', 'font_size': 12, 'font_name': 'Times New Roman', 'border': 1, 'bold': 1})
        fmt_mgr_title = book.add_format({'align': 'center', 'font_size': 14, 'font_name': 'Times New Roman', 'border': 1, 'bold': 1})
        fmt_cell = book.add_format({'align': 'center', 'font_size': 10, 'font_name': 'Arial', 'border': 1})
        fmt_total = book.add_format({'font_size': 10, 'font_name': 'Arial', 'border': 1, 'bold': True, 'align': 'center'})

        # Set title of report
        sheet.merge_range('A1:J1', '"Yyldyz myhmanhanasynda ýaşaýan daşary ýurt raýatlary barada" Maglumat', fmt_mgr_title)

        # Set column names
        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 14)
        sheet.set_column('D:D', 14)
        sheet.set_column('E:E', 8)
        sheet.set_column('F:F', 18)
        sheet.set_column('G:G', 17)
        sheet.set_column('H:H', 16)
        sheet.set_column('I:I', 24)
        sheet.set_column('J:J', 24)

        title_rep = {'A': '#', 'B': 'F.A.A', 'C': 'Otag Belgisi', 'D': 'Doglan Sene','E': 'Jynsy', 'F': 'Raýatlygy'
            , 'G': 'Wizanyň görnüşi', 'H': 'Çagyryjy tarap', 'I': 'Myhmanyň giren wagty', 'J': 'Myhmanyň cykan wagty',
                     }

        for key, value in title_rep.items():
            sheet.write(key + '2', value, fmt_title)

        sheet.set_row(1, 30)

        # Set table data
        count = 1
        row = 2
        for records in migrate_reprt:
            sheet.write(row, 0, count, fmt_cell)  # arrdate
            sheet.write(row, 1, records['fk_gid__surname'], fmt_cell)  # arrtime
            sheet.write(row, 2, records['fk_rid__roomnum'], fmt_cell)  # depdate
            sheet.write(row, 3, records['fk_gid__birthdate'], fmt_cell)  # fk_gid
            sheet.write(row, 4, records['fk_gid__gender'], fmt_cell)  # Country
            sheet.write(row, 5, records['fk_gid__fk_cid__name'], fmt_cell)  # deptime
            sheet.write(row, 6, records['fk_gid__typeofvisa'], fmt_cell)  # Room type
            sheet.write(row, 7, records['fk_gid__company'], fmt_cell)  # Company Name
            sheet.write(row, 8, records['arrdate'].strftime('%d.%m.%Y'), fmt_cell)  # arrdate
            sheet.write(row, 9, records['depdate'].strftime('%d.%m.%Y'), fmt_cell)  # depdate
            row += 1
            count += 1

        book.close()
        # End -> Prepare

        # Construct response
        output.seek(0)
        response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename=guests_report.xlsx"
        response['Cache-Control'] = " max-age=0"
        # End -> Construct
        return response
