import sys, time
from cryptocmd import utils, CmcScraper
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt4.QtCore import *
from PyQt4.QtGui import *

"""
23-03-2018: Definitieve versie CryptoDashboard.
Download laatste prijs gegevens voor cryptocurrencies en plot deze.
"""
class Model():

    def __init__(self):
        pass

    def retrieve(self,coinname):
        coinname=coinname.upper()
        coinID,coinSymbol,coinPrice,coin24Perc,coinMarketCap=None,None,None,None,None
        #coinSymbol=None
        url = 'https://api.coinmarketcap.com/v1/ticker/'
        json_format=utils.get_url_data(url).json()

        for coin in json_format:
            if (coin['symbol']==coinname) or (coin['id']==coinname) or (coin['name']==coinname):
                coinID = coin['id']
                coinSymbol = coin['symbol']
                coinPrice = coin['price_usd']
                coin24Perc = coin['percent_change_24h']
                coinMarketCap = coin['market_cap_usd']
        Controller.passCoin(self,coinID,coinSymbol,coinPrice,coin24Perc,coinMarketCap)


    def download(self,coin_data_id):
        fetcher = CmcScraper(coin_data_id)#(coin['symbol'])

        headers, data = fetcher.get_data()
        print(headers) # test. werkt
        Controller.prepDataframe(self,headers,data)
        #return headers, data

    def get_dataframe(self,headers,data):
        dataframe=pd.DataFrame(data=data, columns=headers)
        dataframe['Date']=pd.to_datetime(dataframe['Date'], errors='raise', format="%d-%m-%Y",dayfirst=True)
        dataframe=dataframe.set_index(dataframe['Date'])
        dataframe=dataframe.drop('Date',1)
        Controller.prepPlot(self,dataframe)
        return dataframe

    def plot(self,coin,dataframe):

       #Aangepaste versie tov stand alone versie. Hier plot maar éen parameter (close).
        
       #if columns==None:
       #   columns=dataframe['Close']
       
       # names, colors
       graphName='{} {}.png'.format(coin,time.strftime("%d-%m-%Y"))
       graphTitle='Cryptocurrency {}'.format(coin)#2e {} en ,columns) 
       colors=['royalblue','gold', 'sandybrown','red','black','orange']
       #for name in matplotlib.colors.cnames.items():
       #    colors.append(name[0])
         
       # ticklabels
       start = dataframe.index[-1]
       end= dataframe.index[0]
       ticklabels=pd.date_range(start, end, freq='QS-JAN')
       
       #actual plotting
       ax=self.figure.add_subplot(111) # fig weggehaald
       ax.clear()
       #for column,color in zip(columns, colors):
       #    plt.plot(dataframe[column],linewidth=1.9,color=color)
       ax.plot(dataframe['Close'],linewidth=3, color= 'red') 
       plt.style.use('ggplot') 
       ax.patch.set_alpha(0.76)
       plt.xticks(ticklabels,rotation=45) # plt. weggehaald
       ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
       ax.set(title=graphTitle, xlabel="Tijd", ylabel="Waarde USD") 
       for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
           ax.get_xticklabels() + ax.get_yticklabels()):
               item.set_fontsize(10)
       plt.grid(b=True, which='major', color='black', linestyle='-')
       plt.grid(b=True, which='minor', color='b', linestyle='dotted',alpha=0.8)
       plt.minorticks_on()
       Controller.displayPlot(self)


class Controller(Model):

    def __init__(self):
        pass

    def start(self):
        View.window(self)

    def clicked(self):
        import webbrowser as wb
        wb.open_new(url)
        print('clicked')

    def Enter_coin(self,coinname):
        coinname=self.CurrencyEdit.text()
        Model.retrieve(self,coinname)

    def passCoin(self,coinid,coinsymbol,coinprice,coin24perc,coinmarketcap):
        self.SummaryCName.setText(coinid) 
        self.SummaryCLabel.setText(coinsymbol) 
        self.SummaryCPrice.setText(coinprice)
        self.Summary24PercentChange.setText(coin24perc)
        self.Summary24MarketCap.setText(coinmarketcap)

    def prepDownl(self):
        coin_data_id=self.SummaryCLabel.text()
        Model.download(self,coin_data_id)

    def prepDataframe(self,headers,data):
        # Check headers
        if len(headers) < 7:
            foutmelding1 = QtGui.QMessageBox.question(self,"Error",
                                                    "Incorrect number of headers. Check download format",
                                                    QtGui.QMessageBox.Yes)

        Model.get_dataframe(self,headers,data)

    def prepPlot(self,dataframe):
        # https://stackoverflow.com/questions/12459811/how-to-embed-matplotlib-in-pyqt-for-dummies#12465861
        coinsymbol=self.SummaryCLabel.text()
        Model.plot(self,coinsymbol,dataframe)

    def displayPlot(self):
        self.canvas.draw()

    def exitApp(self):
        sys.exit()

class View(Model):

    def __init__(self):
        pass

    def window(self):
        app = QApplication(sys.argv)
        win = QWidget()

        windowHeader=QLabel()
        self.figure=Figure()
        Link=QLabel()

        # Titel header en link beneden
        windowHeader.setText('Crypto Dashboard')
        windowHeader.setFont(QFont('SansSerif', 13))
        windowHeader.setAlignment(Qt.AlignCenter)
        emptyHeader=QLabel()
        Link.setText("<A href='https://coinmarketcap.com/'>coinmarketcap</a>")
        Link.setAlignment(Qt.AlignRight)

        #####################################
        # grafiek left panel
        self.canvas=FigureCanvas(self.figure)


        LeftPanelLayout=QHBoxLayout()
        
        graphFrame=QFrame()
        graphFrame.setFrameStyle(QFrame.Panel|QFrame.Sunken)
        graphLayout=QVBoxLayout(graphFrame)
        graphLayout.addWidget(self.canvas)

        
        LeftPanelLayout.addWidget(graphFrame)
        
        #################################
        # Right panel 
        RightPanelLayout=QVBoxLayout()
        RightPanelLayout.setSpacing(3)

        # Bovenste deel: Drie knoppen.
        TopBtnsFrame=QFrame()
        TopBtnsFrame.setFrameStyle(QFrame.Panel|QFrame.Sunken)

        TopBtnsLayout=QFormLayout(TopBtnsFrame)
        
        CurrencyBtn=QPushButton("Find",TopBtnsFrame) # zoekbutton
        self.CurrencyEdit=QLineEdit(TopBtnsFrame)
        self.CurrencyEdit.setText('ltc')
        self.CurrencyEdit.editingFinished.connect(lambda:Controller.Enter_coin(self,self.CurrencyEdit.text()))
        PlotBtn=QPushButton("Plot", TopBtnsFrame) #plot button

        TopBtnsLayout.addRow(CurrencyBtn, self.CurrencyEdit)
        TopBtnsLayout.addRow(PlotBtn)

        RightPanelLayout.addWidget(TopBtnsFrame)
        
        # Middelste deel: summarybox, lijst omgeven waarbij enkele gegevens getoond worden
        SummaryFrame=QFrame()
        SummaryFrame.setFrameShape(QFrame.Panel)
        SummaryFrame.setFrameShadow(QFrame.Sunken)

        SummaryLayout=QFormLayout(SummaryFrame)
        SummaryTitle=QLabel(SummaryFrame).setText('Summary details')
        SummaryEmptyLbl=QLabel()
        SummaryLbl=QLabel(SummaryFrame)
        SummaryLbl.setText("Coin id")
        self.SummaryCName=QLineEdit(SummaryFrame)
        self.SummaryCName.setReadOnly(True)
        SummaryLbl2=QLabel(SummaryFrame)
        SummaryLbl2.setText("Coin label")
        self.SummaryCLabel=QLineEdit(SummaryFrame)
        self.SummaryCLabel.setReadOnly(True)
        SummaryCPriceLbl=QLabel(SummaryFrame)
        SummaryCPriceLbl.setText('Last Price')
        self.SummaryCPrice=QLineEdit(SummaryFrame)
        self.SummaryCPrice.setReadOnly(True)
        Summary24PercentChangeLbl=QLabel(SummaryFrame)
        Summary24PercentChangeLbl.setText('24 hrs Percent Change')
        self.Summary24PercentChange=QLineEdit(SummaryFrame)
        self.Summary24PercentChange.setReadOnly(True)
        Summary24MarketCapLbl=QLabel(SummaryFrame)
        Summary24MarketCapLbl.setText('USD Market Cap')
        self.Summary24MarketCap=QLineEdit(SummaryFrame)
        self.Summary24MarketCap.setReadOnly(True)

        SummaryLayout.addRow(SummaryTitle,SummaryEmptyLbl)
        SummaryLayout.addRow(SummaryLbl, self.SummaryCName)
        SummaryLayout.addRow(SummaryLbl2, self.SummaryCLabel)
        SummaryLayout.addRow(SummaryCPriceLbl, self.SummaryCPrice)
        SummaryLayout.addRow(Summary24PercentChangeLbl, self.Summary24PercentChange)
        SummaryLayout.addRow(Summary24MarketCapLbl, self.Summary24MarketCap)
        # hier komt nog een layout.addRow

        RightPanelLayout.addWidget(SummaryFrame)
        
        # Onderste Deel: BttmButton Box, met daarbij knoppen save en exit
        BttmButtonFrame=QFrame()
        BttmButtonFrame.setFrameStyle(QFrame.Panel|QFrame.Raised)
        BttmButtonLayout=QHBoxLayout(BttmButtonFrame) 
        Exitbutton=QPushButton("Exit")
        
        BttmButtonLayout.addStretch()
        BttmButtonLayout.addWidget(Exitbutton)
        
        RightPanelLayout.addWidget(BttmButtonFrame)

        # Einde Right Panel
        ##################################################

        
        # Overall grid layout   
        gridBox=QGridLayout()

        titleBox=QHBoxLayout()
        titleBox.addWidget(Link)
        titleBox.addStretch()
        titleBox.addWidget(windowHeader)
        titleBox.addStretch()
        titleBox.addWidget(emptyHeader)

        # Grid opbouwen
        gridBox.addLayout(titleBox,0,0)
        gridBox.addLayout(LeftPanelLayout,1,0,3,5)  ##args:QWidget, int r, int c, int rowspan, int columnspan
        gridBox.addLayout(RightPanelLayout,1,6,3,1)

        gridBox.setColumnStretch(0,5) # kolom 0, stretch 5?
        gridBox.setRowStretch(1,1)

        #buttons
        Link.linkActivated.connect(Controller.clicked)
        Exitbutton.clicked.connect(lambda:Controller.exitApp(self))
        CurrencyBtn.clicked.connect(lambda:Controller.Enter_coin(self,self.CurrencyEdit))
        PlotBtn.clicked.connect(lambda:Controller.prepDownl(self))
         
        win.setLayout(gridBox)
        win.setGeometry(25,25,1850,980)
        win.setWindowTitle("Portfolio Dashboard")
        win.show()
        sys.exit(app.exec_())              

if __name__=='__main__':
    c=Controller().start() # nieuw
