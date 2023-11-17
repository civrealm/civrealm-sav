from __future__ import division
import sys
import numpy as np
import pandas as pd
from datetime import datetime, date
import matplotlib.pyplot as plt
from matplotlib import style
import matplotlib.font_manager as fm
import matplotlib.mlab as mlab 
from pandas.plotting import register_matplotlib_converters
import matplotlib.ticker as ticker

register_matplotlib_converters()
FNAME = None

CM = plt.cm.get_cmap('RdYlBu')
COLORS = ['orange', 'red', 'green', 'blue', 'purple', 'hotpink', 'black', 'grey', 'tan', 'darkred', \
                       'cyan', 'darkgreen','yellow','slateblue','lime']
ALPHA = [1, 0.5, 0.25, 0.125]

class PlotMax:
    """
    a union framework of plot

    args:
        capacity: the max curve capacity for each subfigure
        count_cut: the maximum number of subfigures
        style: the background style, default, seaborn-dark, ggplot, bmh, seaborn-bright
        colors: take the color from this list in turn for each line
        alpha: transparency
        fname: the package of Chinese Fonts

    example:
        x1 = [1,2,3,4]
        y1 = [2,3,3,2]
        x2 = [1,3,5]
        y2 = [4,3,2]
        # put two curves into one subplot
        graph = PlotMax(capacity=2, fname='~/msyh.ttf')
        graph.load_data(x1, y1)
        graph.load_data(x2, y2)
        graph.show() # clear data list
        # put two curves into two subplots
        graph.capacity = 1
        graph.load_data(x1, y1)
        graph.load_data(x2, y2)
        graph.show()
    """

    def __init__(self, 
                 capacity=1, 
                 count_cut=100, 
                 style='seaborn-bright',
                 colors=None,
                 alpha=None,
                 fname=None):
        self.capacity = capacity
        self.data_list = []
        self.count_cut = count_cut

        if isinstance(colors, list):
            self.colors = colors
        else:
            self.colors = COLORS
        if isinstance(alpha, list):
            self.alpha = alpha
        else:
            self.alpha = ALPHA
        # if fname is None:
        #     fname = FNAME
        self.fname = fname
        if fname is None:
            self.myfont = fm.FontProperties(size=20)
        else:
            self.myfont = fm.FontProperties(fname=self.fname, size=20)

        plt.style.use(style)

    def get_ax(self, first='col'):
        """
        lay out, find the ax for recent subplot
        """
        if first == 'col':
            col = int(self.subplot_index/self.nrows)
            row = self.subplot_index - self.nrows * col
        elif first == 'row':
            row = int(self.subplot_index/self.ncols)
            col = self.subplot_index - self.ncols * row
        else:
            raise ValueError('no such ax point.')

        if self.ncols == 1 and self.nrows == 1:
            return self.axes
        if self.ncols == 1:
            return self.axes[row]
        if self.nrows == 1:
            return self.axes[col]

        return self.axes[row, col]

    def load_data(self, x=None, y=None, 
             color='hotpink',
             marker='.', 
             label='',
             xlabel='', 
             ylabel='', 
             rotation=0,
             xsize=15,
             ysize=15,
             width=0.5,
             title='',
             xtype='time',
             plot_type='曲线',
             legend=True,
             legendsize=20,
             y2=None,
             label2=None,
             to_pin=False,
             bins=10,
             markerscale=0.5,
             markersize=20,
             xlim=None,
             ylim=None,
             xx=None,
             as_str=False,
             yy=None,
             Z=None,
             legend_loc=0,
             edgecolor='k',
             nan_permit=False,
             titlesize=20,
             barcolor=[],
             scatter_size=[200],
             base=None,
             capacity=None,
             text=False,
             dist=False,
             color2='black',
             dist_curve=False):
        """
        load data into dict
        args:
            x: data list of x-axis
            y: data list of y-axis
            color: set color for this plot data, ['hotpink','blue','green','red','orange','black','yellow']
            marker: point shown style, ['o', '.', ',', 'x', '+', 'v', '^', '<', '>', 's', 'd', '']
            label: legend information
            xlabel: the label of x axis
            ylabel: the label of y axis
            rotation: the rotation degree of x axis
            xsize: the font size of the scale of x axis
            ysize: the font size of the scale of y axis
            title: the title of subfigure
            xtype: abandoned, the type of x axis, time, numeric, what else...
            plot_type: 'curve', 'bar', 'hist', '曲线', '直方图', 'scatter'
            legend: whether to show the label
            legendsize: the font size of legend
            y2: data list of second y axis
            label2: lable of second y axis
            to_pin: translate the Chinese font into pinyin
            bins: the number of bars
            markerscale: the scale of marker
            markersize: the size of marker
            xlim: the limited range of x-axis, example [0, 1]
            ylim: the limited range of y-axis, example [0, 1]
            as_str: change the data type of x-axis to string
            xx: contourf plot 
            yy: contourf plot 
            Z: contourf plot 
            legend_loc: the location of legennd
            edgecolor: the edge color of scattered points
            nan_permit: allow null values in array
            titlesize: the size of title
            barcolor: the color of different scattered points
            scatter_size: the size of different scattered points
            base: the baseline
            capacity: the special setting overwited
            text: whether or not to show text near the points
            dist: used in distribution plot, whether or not to show the distribution of curve
            color2: the color of the second y-axis curve
            dist_curve: used in distribution plot,, whether or not to show the curve of distribution
        """
        try:
            if y is not None:
                assert len(x) >= 0 and len(y)==len(x), 'data length is 0 or the lengh of x is not equal to y'

            try:
                if (isinstance(x[0], str) or isinstance(x[0], np.unicode)) and not isinstance(x[0], date) and not as_str:
                    if len(x[0]) <= 10:
                        x = [datetime.strptime(t, '%Y-%m-%d').date() for t in x]
                    elif len(x[0]) <=12:
                        x = [datetime.strptime(t, '%Y-%m-%d %H').date() for t in x]
                    elif len(x[0]) ==14:
                        x = [datetime.strptime(t, '%Y-%m-%d %H:%M:%S') for t in x]
            except:
                pass

        except Exception as e:
            if nan_permit:
                x = [np.nan]
                y = [np.nan]
            else:
                raise ValueError(e)
        
        if capacity is None:
            capacity = self.capacity
        
        self.data_list.append({'x':x, 'y':y, 'xlim':xlim, 'ylim':ylim, 'marker':marker, 'color':color, 'titlesize':titlesize,\
                               'barcolor':barcolor, 'base':base, 'text':text, 'scatter_size':scatter_size, 'dist':dist,\
                               'legend_loc':legend_loc, 'label':label, 'plot_type':plot_type, 'xlabel':xlabel, 'xx':xx, \
                               'yy':yy, 'Z':Z,'nan_permit':nan_permit, 'capacity':capacity, 'markersize':markersize,\
                               'rotation':rotation,'title':title,'xtype':xtype, 'xsize':xsize, 'ysize':ysize, \
                               'ylabel':ylabel, 'width':width, 'legend':legend, 'bins':bins, 'legendsize':legendsize, \
                               'edgecolor':edgecolor, 'markerscale':markerscale, \
                               'y2':y2, 'label2':label2, 'dist_curve':dist_curve, 'color2':color2})

    def get_row_col(self, count):
        """
        calculate the row and column number according to the number of data passed
        args:
            count: the total number of sub-figures
        """
        if count == 1:
            return 1, 1
        if count <=self.count_cut:
            if count % 2 == 0:
                return int(count/2), 2
            else:
                return int(np.ceil(count/3)), 3
        else:
            return int(np.ceil(np.sqrt(count))), int(np.ceil(np.sqrt(count)))

    def show(self, exchange=False, 
             hspace=0.3, 
             wspace=0.1, 
             dfs={}, 
             grid=True, 
             main_title='', 
             shift=1,
             dpi=30,
             fontsize=30, 
             ncols=None, 
             nrows=None,
             interval=1,
             anchor=(0, 1),
             cut=None,
             legend_loc="upper left",
             first='col',
             figsize=(16,5),
             savepath=''
             ):
        """
        build a figure frame to show data list
        args:
            exchange: False/True, exchange the row number with the column number
            hspace: control the subplot distance in the vertical direction
            wspace: control the subplot distance in the horizontal direction
            dfs: dataframe describe
            grid: whether or not to show the grid lines
            main_title: the main title of figure
            shift: shift the data of x-axis
            dpi: Dots Per Inch
            fontsize: the font size of main title of figure
            ncols: the number of columns
            nrows: the number of rows
            interval: the interval of data of x-axis
            anchor: the location of legend
            cut: cut the x-axis data list
            legend_loc: the default legend location
            first: the first direction to put subfigure, 'col'|'row'
            figsize: the size of figure like (16,5)
            savepath: the save path
        """

        # calculate the number of columns and rows
        data_count = len(self.data_list)
        graph_count = int(np.ceil(data_count/self.capacity))

        if exchange:
            self.ncols, self.nrows = self.get_row_col(graph_count)
        else:
            self.nrows, self.ncols = self.get_row_col(graph_count)

        if len(savepath) > 0:
            plt.switch_backend('agg')

        if ncols is not None:
            self.ncols = ncols
            self.nrows = nrows
            graph_count = self.ncols * self.nrows

        # initialize figure
        _, self.axes = plt.subplots(nrows=self.nrows, ncols=self.ncols, 
                                    figsize=(figsize[0] * self.ncols, figsize[1] * self.nrows))
        plt.subplots_adjust(wspace=wspace, hspace=hspace)

        # initialize the middle variables
        self.subplot_index = 0
        labels = []
        xlabels = []
        extend_dist = []
        handles = []
        plot_type = 'general'
        count = 0
        ax2_hand = None
        
        # loop through all plot datas
        for i in range(data_count):
            ax = self.get_ax(first)
            d = self.data_list[i]
            c = self.colors[count%d['capacity']]
            c_next = self.colors[(count+1)%len(self.colors)]
            if d['x'] is not None:
                xlabels = d['x'] if len(xlabels) < len(d['x']) else xlabels
            
            # build plot ax for different plot type
            if '曲' in d['plot_type'] or '线' in d['plot_type'] or 'line' in d['plot_type']:
                ax_hand = ax.plot(d['x'], d['y'], marker=d['marker'], markersize=d['markersize'], label=d['label'], c=c)
            elif '条' in d['plot_type'] or 'bar' in d['plot_type']:
                ax_hand = ax.bar(d['x'], d['y'], color=d['color'] if len(d['barcolor'])==0 else d['barcolor'], width=d['width'])
            elif '散' in d['plot_type'] or 'scatter' in d['plot_type']:
                if len(d['barcolor']) > 0 and len(d['scatter_size'])==0:
                    ax_hand = ax.scatter(d['x'], d['y'], marker=d['marker'], c=d['barcolor'], cmap=CM, edgecolor=d['edgecolor'])
                    plt.colorbar(ax_hand)
                elif len(d['barcolor']) > 0 and len(d['scatter_size']) > 0:
                    ax_hand = ax.scatter(d['x'], d['y'], marker=d['marker'], s=d['scatter_size'], c=d['barcolor'], \
                                          cmap=CM, edgecolor=d['edgecolor'])
                    plt.colorbar(ax_hand)
                elif len(d['barcolor']) == 0 and len(d['scatter_size']) > 0:
                    ax_hand = ax.scatter(d['x'], d['y'], marker=d['marker'], s=d['scatter_size'], edgecolor=d['edgecolor'])
                else:
                    ax_hand = ax.scatter(d['x'], d['y'], marker=d['marker'], edgecolor=d['edgecolor'])
            elif '雷' in d['plot_type']:
                ax_hand = plt.subplot(111, projection='polar')
                ax_hand.set_rlim(0,12)
                ax_hand.plot(d['x'], d['y'], '.--', label=d['label'], alpha=0.9);
                ax_hand.fill(d['x'], d['y'], alpha=0.2)
            elif '饼' in d['plot_type'] or 'pie' in d['plot_type']:
                ax_hand = ax.pie(d['x'], labels=d['label'], autopct='%1.1f%%', shadow=False, startangle=90)
            elif '盒' in d['plot_type'] or 'box' in d['plot_type']:
                pass
            elif '分布' in d['plot_type'] or '直方' in d['plot_type'] or 'hist' in d['plot_type']:
                plot_type = 'hist'
                n, bins, patches = ax.hist(d['x'], bins=d['bins'], label=d['label'])#, alpha=self.alphas[i % len(self.alphas)]
                if d['dist']:
                    extend_dist.append({'bins':bins, 'y':hy})
                if d['dist_curve']:
                    mu = np.mean(d['x'])
                    sigma = np.std(d['x'])
                    hy = mlab.normpdf(bins, mu, sigma)
                    ax.plot(bins, hy, marker=d['marker'], color=c) #绘制y的曲线 
            elif 'contourf' in d['plot_type'] or '热点' in d['plot_type']:
                ax_hand = plt.contourf(d['xx'], d['yy'], d['Z'], camp=plt.cm.Blues_r)
            else:
                raise 'no corresponding plot type'
                
            if d['y2'] is not None:
                ax2 = ax.twinx()
                ax2_hand = ax2.plot(d['x'], d['y2'], marker=d['marker'], markersize=d['markersize'], \
                                    label=d['label2'], c=d['color2'])
                ax2.tick_params(axis='y', labelsize=d['ysize'])

            if d['legend']:
                if isinstance(d['label'], list):
                    labels = d['label']
                elif isinstance(d['label'], str):
                    labels.append(self.decode(d['label']))
                else:
                    labels.append(d['label'])

                if d['label2'] is not None:
                    labels.append(d['label2'])

                if '散' in d['plot_type'] or 'scatter' in d['plot_type']:
                    handles.append(ax_hand)
                elif plot_type=='hist':
                    pass
                else:
                    handles.append(ax_hand[0])

                if ax2_hand is not None:
                    handles.extend(ax2_hand)

            if d['base'] is not None:
                if d['base']['type'] == 'hline':
                    ax.hlines(d['base']['value'], min(d['x']), max(d['x']), colors=d['base']['color'], \
                              linestyles=d['base']['linestyle'], label=d['base']['label'])
                labels.append(d['base']['label'])

            ax.set_xlabel(d['xlabel'], fontproperties=self.myfont)
            ax.set_ylabel(d['ylabel'], fontproperties=self.myfont)
            ax.tick_params(axis='x', labelsize=d['xsize'])
            ax.tick_params(axis='y', labelsize=d['ysize'])
            plt.xticks(fontproperties=self.myfont)

            if isinstance(d['xlim'], float):
                ax.set_xlim(0, d['xlim'])
                ax.set_ylim(0, d['ylim'])
            elif isinstance(d['xlim'], list):
                ax.set_xlim(d['xlim'][0], d['xlim'][1])
                ax.set_ylim(d['ylim'][0], d['ylim'][1])
                plt.xlim((d['xlim'][0], d['xlim'][1]))
                plt.ylim((d['ylim'][0], d['ylim'][1]))

            ax.set_title(self.decode(d['title']), fontsize=d['titlesize'], fontproperties=self.myfont)
            
            if d['text']:
                for x, y in zip(d['x'], d['y']):
                    if x > 0:
                        ax.text(x, y*1.05, str(d['label']))
            
            if interval > 1:
                temp_x = [xlabels[0]]
                temp_x.extend(xlabels[shift::interval])
                xlabels = temp_x
                ax.xaxis.set_major_locator(ticker.MultipleLocator(interval))
            
            xlabels_str = [str(xs) if cut is None else str(xs)[:cut] for xs in xlabels]
            if d['rotation'] > 0:
                ax.set_xticklabels(xlabels_str, rotation=d['rotation'])
            else:
                if interval > 1:
                    ax.set_xticklabels(xlabels_str)

            if grid:
                ax.xaxis.grid(True, which='major', linestyle='--', color='k') 
                ax.yaxis.grid(True, which='major', linestyle='--', color='k') 

            count += 1

            if  count == d['capacity'] or i == data_count-1:
                count = 0
                self.subplot_index += 1
                if d['legend']:
                    legend_font = fm.FontProperties(fname=self.fname, size=d['legendsize'])
                    ax.legend(handles, labels, fontsize=d['legendsize'], loc=legend_loc, \
                              markerscale=d['markerscale'], shadow=True, bbox_to_anchor=anchor,\
                              prop=legend_font)
                labels = []
                xlabels = []
                handles = []
                
        plt.suptitle(main_title, fontsize=fontsize, fontproperties=self.myfont)

        if graph_count > self.count_cut or len(savepath) > 0:
            print('save figure')
            plt.savefig(savepath, bbox_inches = 'tight', dpi=dpi, pad_inches=0.0)
            plt.close()
        else:
            plt.axis('tight')
            plt.show()

        if d['dist']:
            _, self.axes = plt.subplots(nrows=self.nrows, ncols=self.ncols, 
                                    figsize=(figsize[0] * self.ncols, figsize[1] * self.nrows))
            for i in range(len(extend_dist)):
                d = self.data_list[i]
                ax = self.get_ax(first)
                ax.plot(extend_dist[i]['bins'], extend_dist[i]['y'], label=d['label'], marker=d['marker'], \
                        color=COLORS[i % d['capacity']]) #绘制y的曲线 
            plt.show()

        # clear the data list
        self.data_list = []

        # show the data describe information
        if len(dfs) > 0:
            for key, df in dfs.items():
                print('\n*********', key, '*********')
                print('>>> Data <<<')
                print(df.head())
                print(df.tail())

                print('\n>>> Describe <<<')
                print(df.describe())

    def decode(self, s, coding='Utf-8'):
        if sys.version_info.major < 3:
            return s.decode(coding)
        else:
            return s

if __name__ == '__main__':
    x1 = [1,2,3,4]
    y1 = [2,3,3,2]
    x2 = [1,3,5]
    y2 = [4,3,2]
    # put two curves into one subplot
    graph = PlotMax(capacity=2, fname='~/msyh.ttf')
    graph.load_data(x1, y1)
    graph.load_data(x2, y2)
    graph.show() # clear data list
    # put two curves into two subplots
    graph.capacity = 1
    graph.load_data(x1, y1)
    graph.load_data(x2, y2)
    graph.show()
