import numpy as np
import matplotlib.pyplot as plt

# load array
data = np.loadtxt('data1.csv', delimiter=',')
dataFrec = np.loadtxt('data.csv', delimiter=',')
dataWork= np.loadtxt('dataWork.csv', delimiter=',')
dataWork1= np.loadtxt('dataWork1.csv', delimiter=',')
dataWork2= np.loadtxt('dataWork2.csv', delimiter=',')
dataWork3= np.loadtxt('dataWork3.csv', delimiter=',')
dataWork4= np.loadtxt('dataWork4.csv', delimiter=',')
dataWork5= np.loadtxt('dataWork5.csv', delimiter=',')
dataExample= np.loadtxt('dataExamp.csv', delimiter=',')

# print the array
dataNew= np.array([])

# dataFrec= np.array([])



def ajustarARRAY(dataArray, dataArrayValue, dataArrayValue1, dataArrayValue2, dataArrayValue3, dataArrayValue4, dataArrayValue5, dataArrayValue6):
    dataFinal= np.array([])
    dataFinalValue= np.array([])
    for i in range(23):
        dataFinal= np.append(dataFinal, i)

    dataFinalValue = np.array([])
    dataFinalValue1 = np.array([])
    dataFinalValue2 = np.array([])
    dataFinalValue3 = np.array([])
    dataFinalValue4 = np.array([])
    dataFinalValue5 = np.array([])
    dataFinalValue6 = np.array([])

    for i in range(23):
        count= 0
        sum= 0
        sum1 = 0
        sum2 = 0
        sum3 = 0
        sum4 = 0
        sum5 = 0
        sum6 = 0

        for j in range(2048):
            # print(dataArray[j], j)

            if (dataArray[j] < ( (i+1)*(1000)) ):
                count= count+1
                sum= sum + dataArrayValue[j]
                sum1 = sum1 + dataArrayValue1[j]
                sum2 = sum2 + dataArrayValue2[j]
                sum3 = sum3 + dataArrayValue3[j]
                sum4 = sum4 + dataArrayValue4[j]
                sum5 = sum5 + dataArrayValue5[j]
                sum6 = sum6 + dataArrayValue5[j]


        dataFinalValue= np.append(dataFinalValue, sum/count)
        dataFinalValue1 = np.append(dataFinalValue1, sum1 / count)
        dataFinalValue2 = np.append(dataFinalValue2, sum2 / count)
        dataFinalValue3 = np.append(dataFinalValue3, sum3 / count)
        dataFinalValue4 = np.append(dataFinalValue4, sum4 / count)
        dataFinalValue5 = np.append(dataFinalValue5, sum5 / count)
        dataFinalValue6 = np.append(dataFinalValue6, sum6 / count)

    return dataFinal, dataFinalValue, dataFinalValue1, dataFinalValue2, dataFinalValue3, dataFinalValue4, dataFinalValue5, dataFinalValue6


for i in range(2048):

    sum= 0
    for j in range(50):
        # print('No: ', j, data[i+(246*j)])
        # tempValue= i+(2048*j)
        # temp= data[i+(2048*j)]
        # print(temp)
        sum = sum + data[i+(2048*j)]

    #np.append(dataNew, data[i])
    dataNew= np.append(dataNew, sum / 50)
    # print(dataNew)
    # print('Num: ', i,  sum/50)


# print(data)
# print(dataFrec)
np.savetxt('dataExamp.csv',  dataNew)

# x = np.arange(0,10,0.1)
# y = x*np.c

x= dataExample
x1= dataWork
y= dataFrec


temp, temp1, temp2, temp3, temp4, temp5, temp6, temp7= ajustarARRAY(dataFrec, dataWork, dataExample, dataWork1, dataWork2, dataWork3, dataWork4, dataWork5)



plt.plot(temp,temp1, '-',linewidth=2,color='r', label='BAD')
plt.plot(temp,temp2, 'bo-',linewidth=2,color='g', label='GOOD')
plt.plot(temp,temp3, '-',linewidth=2,color='y', label='BAD' )
plt.plot(temp,temp4, '-',linewidth=2,color='b', label='BAD')
plt.plot(temp,temp5, '-',linewidth=2, color=(0.2,0.1,0.4), label='BAD')
plt.plot(temp,temp6, '-',linewidth=2, color=(0.6,0.1,0.8), label='BAD')
plt.plot(temp,temp7, '-',linewidth=2, color=(0.4,0.1,0.2), label='BAD')

legend = plt.legend(loc='upper right', shadow=True, fontsize='small')
# Put a nicer background color on the legend.
legend.get_frame().set_facecolor('C0')

# plt.legend('label1', 'label2', 'label3')
plt.xlabel('Frequency(Hz)')
plt.ylabel('Noise Nivel')
plt.title('Mathematical study of a sound analyzer spectrum in Engines')
# plt.hold(True)
plt.show()

