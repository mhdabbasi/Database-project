import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets,QtCore, QtGui
from PyQt5.QtWidgets import QDialog, QApplication
import sqlite3
import datetime

from numpy import full

data_base = sqlite3.connect('db/data_base')
DB_cur = data_base.cursor()

#   FIRSTPAGE
class Firstpage(QDialog):
    def __init__(self):
        super(Firstpage, self).__init__()
        loadUi('ui/firstpage.ui', self)
        self.market.clicked.connect(self.gotomarket)
        self.market.setToolTip('فروش')
        self.market.setIcon(QtGui.QIcon('images/sale.png'))
        self.customers.clicked.connect(gotocustomers)
        self.customers.setToolTip('مشتری')
        self.customers.setIcon(QtGui.QIcon('images/customer.png'))
        self.store.clicked.connect(gotostore)
        self.store.setToolTip('انبار')
        self.store.setIcon(QtGui.QIcon('images/storeroom.png'))
        self.history.clicked.connect(self.gotohistory)
        self.history.setToolTip('تاریخچه')
        self.history.setIcon(QtGui.QIcon('images/history.png'))



    def gotomarket(self):
        market = Market()
        widget.addWidget(market)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def gotohistory(self):
        history = History()
        widget.addWidget(history)
        widget.setCurrentIndex(widget.currentIndex()+1)



'-----------------------------------------------------------------------------------------------'
#   MARKET

class Market(QDialog):
    def __init__(self):
        super(Market, self).__init__()
        loadUi('ui/market.ui', self)
        self.m_back.clicked.connect(gotofirst)#دکمه بازگشت
        self.check.clicked.connect(self.checking) #دکمه محاسبه

        self.onlyInt = QtGui.QIntValidator()
        self.amount.setValidator(self.onlyInt)
        self.discount.setValidator(self.onlyInt)


    def checking(self):#عملیات محاسبه
        name = self.name.text()
        amount = self.amount.text()
        facture = self.facture.text()
        national = self.national.text()
        tracking = self.tracking.text()
        discount = self.discount.text()
        
        tracking = None if len(tracking)==0 else str(tracking)
        discount = 0 if len(discount)==0 else int(discount)
        amount =  0 if len(amount)==0 else int(amount)
        facture = None if len(facture)==0 else int(facture)
        name = None if len(name)==0 else name
        national = None if len(national)==0 else national
        goods_price = DB_cur.execute("SELECT price FROM goods WHERE name=?",(name,)).fetchall()
        goods_price = int(goods_price[0][0]) if len(goods_price)!=0 else 0
        total_price = goods_price*int(amount) - int(discount)

        try:
            DB_cur.execute('''INSERT INTO sale('tracking','time',
                            'amount','invoice','discount','total_price','id','name') 
                            VALUES (?,?,?,?,?,?,?,?) ''',
                            (tracking,datetime.datetime.now(),amount,facture,discount,total_price,national,name,))
            data_base.commit()

            self.sellerror.setStyleSheet("color:  rgb(48, 112, 69)")
            out = "انجام شد، هزینه کل:" + str(total_price)
            self.sellerror.setText(out)

        except Exception as e:
            e = str(e)
            self.sellerror.setStyleSheet("color: rgb(149, 40, 18)")
            if e[:8]=='NOT NULL': 
                self.sellerror.setText("   لطفا اطلاعات را کامل کنید")
            elif e[:6]=='UNIQUE':
                self.sellerror.setText("شماره فاکتور تکراری است")
            elif e[:5]=='CHECK':  # errors for checks
                self.sellerror.setText(e[25:])
            else:  # errors for triggers
                self.sellerror.setText(e)



'-----------------------------------------------------------------------------------------------'
#   CUSTOMERS

class Customers(QDialog):
    def __init__(self):
        super(Customers, self).__init__()
        loadUi('ui/customers.ui', self)
        self.c_back.clicked.connect(gotofirst)
        self.c_add.clicked.connect(self.goto_addcustomer)
        self.c_searchbutton.clicked.connect(self.search)

        self.c_search.setPlaceholderText('نام مشتری را وارد کنید')
        
        ## customer info
        name_id = DB_cur.execute("SELECT name,id FROM customer").fetchall()
        self.table = QtWidgets.QTableWidget()
        self.table.setRowCount(len(name_id))
        self.table.setColumnCount(2)
        self.table.setColumnWidth(0,142)
        self.table.setColumnWidth(1,142)
        self.table.setHorizontalHeaderLabels(['نام','کد'])
        for i,ni in enumerate(name_id):
            item1 = QtWidgets.QTableWidgetItem(str(ni[0]))
            item2 = QtWidgets.QTableWidgetItem(str(ni[1]))
            item1.setFlags(QtCore.Qt.ItemIsEnabled)
            item2.setFlags(QtCore.Qt.ItemIsEnabled)
            self.table.setItem( i,0,item1 )
            self.table.setItem( i,1,item2 )
        self.scrollArea.setWidget(self.table)

    def goto_addcustomer(self):
        add = Addcustomer()
        widget.addWidget(add)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def search(self):
        customer = self.c_search.text()
        names = DB_cur.execute("SELECT * FROM customer WHERE name=?",(str(customer),)).fetchall()
        self.found_table.setColumnCount(1)
        self.found_table.setColumnWidth(0,235)
        if len(names)==0:
            self.found_table.setRowCount(1)
            item = QtWidgets.QTableWidgetItem("موردی یافت نشد!")
            item.setFlags(QtCore.Qt.ItemIsEnabled)
            self.found_table.setItem(0,0,item)
        else:
            self.found_table.setRowCount(len(names))
            for i,cust in enumerate(names):
                out = ''
                for info_name,info in zip(['کد ملی','نام','آدرس','شماره حساب','شماره تلفن'], cust):
                    if info!=None:
                        if info_name=='ادرس' and len(info)>20:
                            new_info = '%s\n%s'%(info[:20],info[20:])
                            out += '%s: %s\n'%(info_name, str(new_info))
                        else:
                            out += '%s: %s\n'%(info_name, str(info))
                self.found_table.setRowHeight(i,180)
                item = QtWidgets.QTableWidgetItem(out)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.found_table.setItem(i,0,item)






'-----------------------------------------------------------------------------------------------'
#   STORE

class Store(QDialog):
    def __init__(self):
        super(Store, self).__init__()
        loadUi('ui/store.ui', self)
        self.s_back.clicked.connect(gotofirst)#دکمه بازگشت
        self.s_add.clicked.connect(self.goto_addsttuf)
        self.storetab.setCurrentIndex(0)
        self.storetable.setColumnCount(3)
        self.storetable.setColumnWidth(0, 137)
        self.storetable.setColumnWidth(1, 145)
        self.storetable.setColumnWidth(2, 148)
        self.storetable.setHorizontalHeaderLabels(['نام کالا','موجودی','قیمت'])    
        self.storetab.currentChanged.connect(self.tabchanged)
        self.tabindex = self.storetab.currentIndex()
        self.show_table()



    def goto_addsttuf(self):
        add = Addsttuf()
        widget.addWidget(add)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def tabchanged(self):# با تغییر تب ،index تب جدید رو میگیره
        self.tabindex = self.storetab.currentIndex()
        self.show_table()
    
    def show_table(self):
        group_name_dict = {2:'ابزار',
                           3:'مصالح ساختمان',
                           1:'لوله و اتصالات'}
        if self.tabindex == 0:
            grouped_goods = DB_cur.execute("SELECT name,price,amount FROM goods").fetchall()
        else:
            grouped_goods = DB_cur.execute("SELECT name,price,amount FROM goods WHERE group_name=?",(group_name_dict[self.tabindex],)).fetchall()
        self.storetable.setRowCount(len(grouped_goods))
        for i,row in enumerate(grouped_goods):
            item1 = QtWidgets.QTableWidgetItem(str(row[1]))
            item2 = QtWidgets.QTableWidgetItem(str(row[2]))
            item3 = QtWidgets.QTableWidgetItem(str(row[0]))
            item1.setFlags(QtCore.Qt.ItemIsEnabled)
            item2.setFlags(QtCore.Qt.ItemIsEnabled)
            item3.setFlags(QtCore.Qt.ItemIsEnabled)
            self.storetable.setItem(i,2, item1)
            self.storetable.setItem(i,1, item2)
            self.storetable.setItem(i,0, item3)


'-----------------------------------------------------------------------------------------------'
#   HISTORY

class History(QDialog):
    def __init__(self):
        super(History, self).__init__()
        loadUi('ui/history.ui', self)
        self.h_back.clicked.connect(gotofirst)#دکمه بازگشت

        self.hist_table.setColumnCount(8)
        self.hist_table.setColumnWidth(0, 100)
        self.hist_table.setColumnWidth(1, 80)
        self.hist_table.setColumnWidth(2, 100)
        self.hist_table.setColumnWidth(3, 100)
        self.hist_table.setColumnWidth(4, 200)
        self.hist_table.setColumnWidth(5, 70)
        self.hist_table.setColumnWidth(6, 100)
        self.hist_table.setColumnWidth(7, 100)
        self.hist_table.setHorizontalHeaderLabels(
            ['شماره فاکتور', 'کد مشتری', 'نام کالا','هزینه نهایی', 'تاریخ','مقدار','شماره پیگیری','تخفیف'])

        self.radioButton.val = 'invoice'
        self.radioButton.toggled.connect(self.sort)
        self.show_sorted('invoice')
        self.radioButton_2.val = 'id'
        self.radioButton_2.toggled.connect(self.sort)
        self.radioButton_3.val = 'time'
        self.radioButton_3.toggled.connect(self.sort)
        self.radioButton_4.val = 'name'
        self.radioButton_4.toggled.connect(self.sort)
    
    def sort(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            self.show_sorted(radioButton.val)

    def show_sorted(self,RB_value):
        sorted_sale = DB_cur.execute('''SELECT invoice,id,name,total_price,time,amount,tracking,discount
                                        FROM sale ORDER BY %s DESC'''%str(RB_value)).fetchall()
        self.hist_table.setRowCount(len(sorted_sale))
        for r,sale in enumerate(sorted_sale):
            for c,col in enumerate(sale):
                item = QtWidgets.QTableWidgetItem(str(col))
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.hist_table.setItem(r, c, item)





'-----------------------------------------------------------------------------------------------'
# ADD CUSTOMER

class Addcustomer(QDialog):
    def __init__(self):
        super(Addcustomer, self).__init__()
        loadUi('ui/addcustomer.ui', self)
        self.addcustomer_back.clicked.connect(gotocustomers)#دکمه بازگشت به صفحه مشتریان
        self.c_check.clicked.connect(self.checking) #دکمه بررسی اطلاعات مشتری وارد شده

        self.onlyInt = QtGui.QIntValidator()
        self.nationalcode.setValidator(self.onlyInt)


    def checking(self):#عملیات بررسی اطلاعات وارد شده
        fullname = self.fullname.text()
        accnumber = self.accountnumber.text()
        phone = self.phone.text()
        national = self.nationalcode.text()
        address = self.address.text()
        self.c_condition.setStyleSheet("color: rgb(149, 40, 18)")

        accnumber = None if len(accnumber)==0 else accnumber
        address = None if len(address)==0 else address
        fullname = None if len(fullname)==0 else fullname
        phone = None if len(phone)==0 else str(phone)
        national = None if len(national)==0 else national

        try:
            DB_cur.execute('''INSERT INTO customer ('id','name','address','acc_num','phone_num')
                                VALUES (?,?,?,?,?)''',(national,fullname,address,accnumber,phone))
            data_base.commit()
            self.c_condition.setStyleSheet("color: rgb(48, 112, 69)")
            self.c_condition.setText("اطلاعات مشتری با موفقیت ثبت شد")
        except Exception as e:
            e = str(e)
            if e[:8]=='NOT NULL':
                self.c_condition.setText("          لطفا اطلاعات را کامل کنید")
            elif e[:6]=='UNIQUE':
                self.c_condition.setText("   اطلاعات مشتری قبلا ثبت شده است")

                


'-----------------------------------------------------------------------------------------------'
# ADD STTUF

class Addsttuf(QDialog):
    def __init__(self):
        super(Addsttuf, self).__init__()
        loadUi('ui/addsttuf.ui', self)
        self.addsttuf_back.clicked.connect(gotostore) #دکمه بازگشت به صفحه انبار
        self.sttuf_check.clicked.connect(self.checking) #دکمه بررسی اطلاعات کالای وارد شده

        self.onlyInt = QtGui.QIntValidator()
        self.price.setValidator(self.onlyInt)
        self.available.setValidator(self.onlyInt)


    def checking(self):#بررسی اطلاعات کالا
        sttufname = self.sttufname.text()
        groupname = self.groupname.currentText()
        available = self.available.text()
        unit = self.unit.currentText()
        price = self.price.text()

        sttufname = None if (len(sttufname)==0) else str(sttufname)
        available = int(available) if len(available)!=0 else None
        price = int(price) if len(price)!=0 else None

        try:
            DB_cur.execute("INSERT INTO goods(price,name,amount,group_name,unit) VALUES (?,?,?,?,?)",
            (price,sttufname,available,groupname,unit,))
            data_base.commit() 
            self.sttuf_condition.setStyleSheet("color: rgb(48, 112, 69)") #تغییر رنگ نوشته
            self.sttuf_condition.setText("                    کالا اضافه شد")

        except Exception as e:
            e = str(e)
            self.sttuf_condition.setStyleSheet("color: rgb(149, 40, 18)")
            if e[:8]=='NOT NULL':
                self.sttuf_condition.setText("          لطفا اطلاعات را کامل کنید")
            elif e[:6]=='UNIQUE':
                old_available = int(DB_cur.execute("SELECT amount FROM goods WHERE name=?",(sttufname,)).fetchall()[0][0])
                DB_cur.execute("UPDATE goods SET price=?, amount=?, group_name=?, unit=? WHERE name=?",
                                (price,available+old_available,groupname,unit,sttufname))
                data_base.commit()
                self.sttuf_condition.setStyleSheet("color: rgb(48, 112, 69)") #تغییر رنگ نوشته
                self.sttuf_condition.setText("                    کالا بروز رسانی شد")
                
            else:
                self.sttuf_condition.setText(e[25:])




'-----------------------------------------------------------------------------------------------'
# OTHER FUNCTIONS

def gotofirst():
    first = Firstpage()
    widget.addWidget(first)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def gotocustomers():
    customer = Customers()
    widget.addWidget(customer)
    widget.setCurrentIndex(widget.currentIndex()+1)



def gotostore():
    store = Store()
    widget.addWidget(store)
    widget.setCurrentIndex(widget.currentIndex()+1)



'-----------------------------------------------------------------------------------------------'
#  MAIN

app = QApplication(sys.argv)
app.setLayoutDirection(QtCore.Qt.RightToLeft)
first = Firstpage()
widget = QtWidgets.QStackedWidget()
widget.addWidget(first)
widget.setFixedHeight(565)
widget.setFixedWidth(775)
widget.show()
try:
    sys.exit(app.exec_())
except:
    print("Exiting")

