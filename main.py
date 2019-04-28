# 我采用requests库
import requests
import time
import dbop
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np

# 用来获取 时间戳
def gettime():
    return int(round(time.time() * 1000))

def Spider1():
    dbop.sqlclear(1)
    headers = {}
    keyvalue = {}
    url = 'http://data.stats.gov.cn/easyquery.htm'
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                            'AppleWebKit/537.36 (KHTML, like Gecko)' \
                            ' Chrome/71.0.3578.98 Safari/537.36'

    keyvalue['m'] = 'QueryData'
    keyvalue['dbcode'] = 'hgnd'
    keyvalue['rowcode'] = 'zb'
    keyvalue['colcode'] = 'sj'
    keyvalue['wds'] = '[]'
    keyvalue['dfwds'] = '[{"wdcode":"zb","valuecode":"A0303"}]'
    keyvalue['k1'] = str(gettime())

    s = requests.session()
    r = s.post(url, params=keyvalue, headers=headers)
    print(r.status_code)

    keyvalue['dfwds'] = '[{"wdcode":"sj","valuecode":"LAST20"}]'
    r = s.post(url, params=keyvalue, headers=headers)
    r1 = r.json()
    table = r1['returndata']['datanodes']

    # 定义五个list来储存数据
    yearlist = []
    totallist = []
    younglist = []
    midlist = []
    oldlist = []

    for node in table:
        year = node['code'][-4:]
        dataclass = int(node['code'][9])
        data = node['data']
        ppdata = data['strdata']
        if year == '2018':
            continue

        if dataclass == 1:  # 第一轮储存年份和总人口数据
            yearlist.append(year)
            totallist.append(int(ppdata))
        elif dataclass == 2:  # 第二轮储存每年的低龄人口
            younglist.append(int(ppdata))
        elif dataclass == 3:  # 第三轮储存每年的中龄人口
            midlist.append(int(ppdata))
        elif dataclass == 4:  # 第四轮储存每年的老龄人口
            oldlist.append(int(ppdata))

    nodelist =[]

    for i in range(19):
        node = []
        node.append(yearlist[i])
        node.append(totallist[i])
        node.append(younglist[i])
        node.append(midlist[i])
        node.append(oldlist[i])
        nodelist.append(node)

    dbop.sqlwrite(1, nodelist)


def Spider2():
    dbop.sqlclear(2)
    headers = {}
    keyvalue = {}
    url = 'http://data.stats.gov.cn/easyquery.htm'
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                            'AppleWebKit/537.36 (KHTML, like Gecko)' \
                            ' Chrome/71.0.3578.98 Safari/537.36'

    keyvalue['m'] = 'QueryData'
    keyvalue['dbcode'] = 'hgnd'
    keyvalue['rowcode'] = 'zb'
    keyvalue['colcode'] = 'sj'
    keyvalue['wds'] = '[]'
    keyvalue['dfwds'] = '[{"wdcode":"zb","valuecode":"A020B"}]'
    keyvalue['k1'] = str(gettime())

    s = requests.session()
    r = s.post(url, params=keyvalue, headers=headers)
    print(r.status_code)
    r1 = r.json()
    table = r1['returndata']['datanodes']

    yearlist = []
    amlist = []
    rmlist = []
    umlist = []
    ailist = []
    rilist = []
    uilist = []

    for node in table:
        year = node['code'][-4:]
        if year == "2018":  # 2018年为空数据，不存储
            continue

        dataclass = int(node['code'][9])

        if dataclass > 6:
            break
        data = node['data']
        cdata = data['strdata']

        if dataclass == 1:  # 第一轮储存年份和居民消费总水平
            yearlist.append(year)
            amlist.append(int(cdata))
        elif dataclass == 2:  # 第二轮储存农村居民消费水平
            rmlist.append(int(cdata))
        elif dataclass == 3:  # 第三轮储存城市居民消费水平
            umlist.append(int(cdata))
        elif dataclass == 4:  # 第四轮储存居民消费总指数
            ailist.append(float(cdata))
        elif dataclass == 5:  # 第五轮输出农村居民消费指数
            rilist.append(float(cdata))
        elif dataclass == 6:  # 第六轮储存城市居民消费总指数
            uilist.append(float(cdata))

    nodelist = []

    for i in range(9):
        node = []
        node.append(yearlist[i])
        node.append(amlist[i])
        node.append(rmlist[i])
        node.append(umlist[i])
        node.append(ailist[i])
        node.append(rilist[i])
        node.append(uilist[i])
        nodelist.append(node)

    dbop.sqlwrite(2, nodelist)


def makeplot_1():
    relist = []
    year = ['1999', '2000', '2001', '2002', '2003', '2004', '2005', '2006',
            '2007', '2008', '2009', '2010', '2011', '2012', '2013', '2014',
            '2015', '2016', '2017']
    total = []
    young = []
    mid = []
    old = []

    for y in year:  # 从数据库读取每年的数据
        re = dbop.sqlread("structure", "year", y)
        relist.append(re)

    re2016 = dbop.sqlread("structure", "year", "2016")  # 读取2016年的数据
    data2016 = re2016[0]

    for ysta in relist:
        sta = ysta[0]
        total.append(sta[1])
        young.append(sta[2])
        mid.append(sta[3])
        old.append(sta[4])

    ypro = []
    mpro = []
    opro = []
    for i in range(19):  # 计算每年的人口占比
        ypro.append(young[i] / total[i])
        mpro.append(mid[i] / total[i])
        opro.append(old[i] / total[i])

    slices = [data2016[2], data2016[3], data2016[4]]
    category = ['0-14', '15-64', '65+']
    cols = ['LightCoral', 'MediumSpringGreen', 'DeepSkyBlue']
    fig = plt.figure(num=1, figsize=(20, 8), dpi=60)  # 配置窗口及子图
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
    # 配置饼图
    ax1.pie(slices,
            labels=category,
            colors=cols,
            startangle=180,
            shadow=True,
            explode=(0, 0, 0.2),
            autopct='%1.1f%%')
    ax1.set_title('The structure of 2016', fontsize=20)
    # 配置折线图
    ax2.plot(year, ypro, label='young', color='r')
    ax2.plot(year, mpro, label='mid', color='g')
    ax2.plot(year, opro, label='old', color='b')
    ax2.set_title('The tendency of last 20 years', fontsize=20)
    ax2.set_xlabel('Year')
    ax2.set_ylabel('Proportion(%)')
    xmajorlocator = MultipleLocator(1)  # 配置刻度
    ymajorlocator = MultipleLocator(0.04)
    ax2.xaxis.set_major_locator(xmajorlocator)
    ax2.yaxis.set_major_locator(ymajorlocator)
    ax2.xaxis.grid(True, which='major')  # 绘制网格线
    ax2.yaxis.grid(True, which='major')
    ax2.legend(loc=0)
    plt.suptitle("The Age Structure", fontsize=30)
    plt.show()

def makeplot_2():
    relist = []
    year = ['2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017']
    index = np.arange(9)
    amlist = []
    rmlist = []
    umlist = []
    ailist = []
    rilist = []
    uilist = []

    for y in year:
        relist.append(dbop.sqlread("consumption", "year", y))

    for ysta in relist:
        sta = ysta[0]
        amlist.append(sta[1])
        rmlist.append(sta[2])
        umlist.append(sta[3])
        ailist.append(sta[4])
        rilist.append(sta[5])
        uilist.append(sta[6])

    fig = plt.figure(num=2, figsize=(20, 10), dpi=60)  # 配置窗口及子图
    ax1 = fig.add_subplot(2, 2, 1)  # 绘制四个子图
    ax2 = fig.add_subplot(2, 2, 2)
    ax3 = fig.add_subplot(2, 2, 3)
    ax4 = fig.add_subplot(2, 2, 4)

    # 子图1表示居民消费水平随时间的变化
    wbar = 0.2
    ax1.bar(index+2009, umlist, label='urban consumption', color='MediumSpringGreen', width=wbar)  # 为了把几个柱子分开
    ax1.bar(index+2009+wbar, amlist, label='average consumption', color='DarkTurquoise', width=wbar)
    ax1.bar(index+2009+wbar*2, rmlist, label='rural consumption', color='Crimson', width=wbar)
    ax1.legend()
    ax1.set_title('The consumption level of last 10 years', fontsize=15)
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Consumption Level(10^4 yuan)', fontsize=10)
    xmajorlocator = MultipleLocator(1)  # 配置刻度
    ymajorlocator = MultipleLocator(3000)
    ax1.xaxis.set_major_locator(xmajorlocator)
    ax1.yaxis.set_major_locator(ymajorlocator)

    # 子图2表示城市居民消费水平与农村居民消费水平的比值随时间的关系
    complist = []
    for i in range(9):
        complist.append(umlist[i]/rmlist[i])
    ax2.plot(year, complist, color='m', label='Times', linewidth=5)
    ax2.legend()
    ax2.set_title("urban consumption level divided by rural consumption level", fontsize=15)
    ax2.xaxis.grid(True, which='major')  # 绘制网格线
    ax2.yaxis.grid(True, which='major')

    # 子图3表示居民消费水平增长指数随时间的变化（相比于上一年）
    ax3.plot(year, ailist, color='r', label='average growth index')
    ax3.plot(year, rilist, color='g', label='rural growth index')
    ax3.plot(year, uilist, color='b', label='urban growth index')
    ax3.legend()
    ax3.set_title('The growth rate of last 10 years(compare with last year)', fontsize=15)
    ax3.set_xlabel('Year')
    ax3.set_ylabel('growth rate(%)', fontsize=10)
    xmajorlocator = MultipleLocator(1)  # 配置刻度与网格线
    ymajorlocator = MultipleLocator(1)
    ax3.xaxis.set_major_locator(xmajorlocator)
    ax3.yaxis.set_major_locator(ymajorlocator)
    ax3.xaxis.grid(True, which='major')
    ax3.yaxis.grid(True, which='major')

    # 子图4表示农村与城市居民的消费水平增长率的差值
    difflist = []
    for i in range(9):  # 计算差值
        difflist.append(rilist[i]-uilist[i])

    diff_tmp = []

    for i in range(0, 17, 2):  # 给差值序列进行线性插值，不影响所需要的各年份的数据，但可以使得绘图模块的填充功能正确运行
        diff_tmp.append(difflist[int(i/2)])
        if i < 16:
            diff_tmp.append((difflist[int(i/2)]+difflist[int(i/2)+1])/2)
    diff_tmp[3] = diff_tmp[5] = diff_tmp[7] = 2.0  # 这三个值需要手动修改，但它们不是真实统计到的数据，只是实现功能需要的插值

    # 插值得到的序列如下，其中偶数位上的数据就是我们搜集到的真实数据，奇数位置上的数据由插值得到
    # diff = [1.3, 0.4, -0.5, 2.0, 4.7, 2.0, 1.7, 2.0, 3.3, 3.8, 4.3, 4.2, 4.1, 3.95, 3.8, 3.3, 2.8]
    diff1 = np.array(diff_tmp)

    # 线性插值的年份序列，年份也进行了线性插值
    year1 = ['2009', '2009.5', '2010', '2010.5', '2011', '2011.5', '2012', '2012.5', '2013',
             '2013.5', '2014', '2014.5', '2015', '2015.5', '2016', '2016.5', '2017']
    ax4.plot(year1, diff1, label='growth rate difference', color='k')
    ax4.legend()
    ax4.set_title('The growth rate difference between rural and urban', fontsize=15)
    ax4.fill_between(year1, diff1, 2, where=diff1 >= 2, color='r', alpha=0.5)
    ax4.fill_between(year1, diff1, 2, where=diff1 <= 2, color='g', alpha=0.5)
    ax4.set_xlabel('Year')
    ax4.set_ylabel('growth rate difference(%)', fontsize=10)
    ax4.set_xticks([])  # 去除坐标轴刻度
    ax4.set_xticks(year)  # 设置坐标轴刻度
    ymajorlocator = MultipleLocator(0.5)
    ax4.yaxis.set_major_locator(ymajorlocator)
    ax4.xaxis.grid(True, which='major')
    ax4.yaxis.grid(True, which='major')

    plt.suptitle("Consumption Level", fontsize=40)
    plt.show()


if __name__ == '__main__':
    Spider1()
    Spider2()
    makeplot_1()
    makeplot_2()

