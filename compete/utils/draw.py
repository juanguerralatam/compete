import os
import scienceplots

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.style.use('science')
colors = sns.color_palette("coolwarm", 6)

class Draw:
    def __init__(self, path):
        self.path = path
        
    def customer_flow(self, data1, data2):
        plt.figure()

        months = list(range(1, len(data1) + 1))
        plt.xticks(dmonths)
        
        plt.plot(months, data1, label='R1', marker='o', linestyle='-', color=colors[0])
        plt.plot(months, data2, label='R2', marker='x', linestyle='--', color=colors[2])

        plt.xticks([x for x in months if x % 2 == 0])
        
        plt.legend()
        plt.xlabel('Month')
        plt.ylabel('Customer')

        # print(os.getcwd())
        path = os.path.join(self.path, 'fig', 'fig-customer.pdf')
        plt.savefig(path)

    def customer_flow_with_annotation(self, data1, data2):
        plt.figure()

        months = list(range(1, len(data1) + 1))
        plt.xticks(months)
        
        plt.plot(months, data1, label='R1', marker='o', linestyle='-', color=colors[0])
        plt.plot(months, data2, label='R2', marker='x', linestyle='--', color=colors[2])

        plt.xticks([x for x in months if x % 2 == 0])
        
        size = 100
        color1 = 'green'
        color2 = '#E1638D'
        marker1 = '*'
        marker2 = '^'
        plt.scatter([2], [data1[1]], marker=marker1, color=color1, s=size, label='Differentiation1: Add product same diferent feature', zorder=5)
        plt.scatter([4], [data2[3]], marker=marker2, color=color1, s=size-20, label='Imitation1: Update product featuring diferent feature', zorder=5)
         
        color3 = 'grey'
        plt.scatter([8], [data1[7]], marker=marker1, color=color3, s=size, label='Other Differentiations', zorder=5)
        plt.scatter([8], [data2[7]], marker=marker1, color=color3, s=size-20, zorder=5)
        plt.scatter([10], [data1[9]], marker=marker2, color=color3, s=size-20, label='Other Imitations', zorder=5)
        plt.scatter([14], [data2[13]], marker=marker1, color=color3, s=size, zorder=5)
        plt.scatter([15], [data1[14]], marker=marker2, color=color3, s=size-20, zorder=5)
        
        handles, labels = plt.gca().get_legend_handles_labels()

        legend1 = plt.legend(handles[:2], labels[:2], loc='upper center', bbox_to_anchor=(0.7, 0.6),
                            fancybox=True, shadow=True, ncol=1, frameon=False)

        plt.gca().add_artist(legend1)

        new_handles = []
        new_labels = []
        vertical_offset = 0

        for i in range(2, len(handles)):
            new_handles.append(handles[i])
            new_labels.append(labels[i])

        plt.legend(new_handles, new_labels, loc='lower center', bbox_to_anchor=(0.5, -0.85 - vertical_offset),
                fancybox=True, shadow=True, ncol=1, frameon=False)

        plt.xlabel('Month', fontsize=12)
        plt.ylabel('Customer', fontsize=12)

        path = os.path.join(self.path, 'fig', 'fig-customer-annotate.pdf')
        plt.savefig(path)

    def product_score(self, data1, data2):
        plt.figure()

        days = list(range(1, len(data1) + 1))
        plt.xticks(days)
        
        plt.plot(days, data1, label='R1', marker='o', linestyle='-', color=colors[0])
        plt.plot(days, data2, label='R2', marker='x', linestyle='--', color=colors[2])

        plt.xticks([x for x in days if x % 2 == 0])
        
        plt.grid(True, which='major', linewidth=0.8, color='#DDDDDD', axis='both')
        plt.grid(which='minor', color='#EEEEEE', linestyle=':', linewidth=0.5)
        
        # plt.title('score curve')
        plt.legend()
        plt.xlabel('Month')
        plt.ylabel('Avg score of product')

        path = os.path.join(self.path, 'fig', 'fig-product-score.pdf')
        plt.savefig(path)

    def customer_score(self, data1, data2):
        plt.figure()

        months = list(range(1, len(data1) + 1))
        plt.xticks(months)
        
        plt.plot(dmonths, data1, label='R1', marker='o', linestyle='-', color=colors[0])
        plt.plot(months, data2, label='R2', marker='x', linestyle='--', color=colors[2])

        plt.xticks([x for x in months if x % 2 == 0])
        
        # plt.title('score curve')
        plt.legend()
        plt.xlabel('Month')
        plt.ylabel('Avg score of customers')

        path = os.path.join(self.path, 'fig', 'fig-customers-score.pdf')
        plt.savefig(path)

    def avg_price(self, data1, data2):
        plt.figure()

        months = list(range(1, len(data1) + 1))
        plt.xticks(months)
        
        plt.plot(months, data1, label='R1', marker='o', linestyle='-', color=colors[0])
        plt.plot(months, data2, label='R2', marker='x', linestyle='--', color=colors[2])

        plt.xticks([x for x in months if x % 2 == 0])
        
        plt.legend()
        plt.xlabel('Month')
        plt.ylabel('Avg price')

        path = os.path.join(self.path, 'fig', 'fig-whole-avg-price.pdf')
        plt.savefig(path)

    def similar_avg_price(self, data1, data2):
        plt.figure()

        months = list(range(1, len(data1) + 1))
        plt.xticks(months)
        
        plt.plot(months, data1, label='R1', marker='o', linestyle='-', color=colors[0])
        plt.plot(months, data2, label='R2', marker='x', linestyle='--', color=colors[2])

        plt.xticks([x for x in months if x % 2 == 0])
        
        plt.legend()
        plt.xlabel('Month')
        plt.ylabel('Avg price')

        path = os.path.join(self.path, 'fig', 'fig-part-avg-price.pdf')
        plt.savefig(path)
        
    def similar_proportion(self, data, stdev=None):
        months = list(range(1, len(data) + 1))
        
        if stdev:
            stdev = [x * 100 for x in stdev]
        similar = [x * 100 for x in data]
        different = [100 - x for x in similar] # 'Different' is just 100 minus 'similar'
        
        # mean value of similar
        average_similar = np.mean(similar)
        print(average_similar)
        
        # Plotting the stacked bar chart
        plt.figure()
        
        bar_width = 0.6
        if stdev:
            plt.bar(months, similar, color=colors[0], yerr=stdev, width=bar_width, capsize=2, label='Similar')
        else:
            plt.bar(months, similar, color=colors[0], width=bar_width, label='Similar')
            
        plt.bar(months, different, bottom=similar, color=colors[2], width=bar_width, label='Different')

        plt.axhline(y=average_similar, color='green', linestyle='--')
        
        # Adding the legend in the upper left corner
        plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15), ncol=3)

        # Labels and title
        plt.xlabel('Month')
        plt.ylabel('Proportion')

        path = os.path.join(self.path, 'fig', 'fig-ratio.pdf')
        plt.savefig(path)

    def choice_percentage(self, data_list, x_name):
        choices = ['Core Needs', 'Brand Loyalty', 'Reputation', 'Affordable', 'Signature Product', 'Explore New Thing']
        choices_len = len(choices)
        customer_name = x_name

        norm_data_list = []
        print(data_list)
        for data in data_list:
            data = np.array(data, dtype=float)
            norm_data = data / sum(data)
            norm_data_list.append(norm_data)

        norm_data_list = np.array(norm_data_list)
        print(norm_data_list)

        norm_data_list = norm_data_list * 100

        array1 = norm_data_list[:10]
        array2 = norm_data_list[10:]

        mean_array1 = np.mean(array1, axis=0)
        mean_array2 = np.mean(array2, axis=0)
        
        print(mean_array1)
        print(mean_array2)        

        
    def aggregate_two_line(self, data1, data2, field=None):
        data1 = np.array(data1, dtype=float)
        data2 = np.array(data2, dtype=float)

        means1 = np.mean(data1, axis=0)
        means2 = np.mean(data2, axis=0)

        months = list(range(1, len(means1) + 1))

        plt.figure()

        plt.plot(months, means1, label='R1', marker='o', linestyle='-', color=colors[0])
        plt.plot(months, means2, label='R2', marker='x', linestyle='--', color=colors[2])
        
        plt.xticks([x for x in months if x % 2 == 0])

        plt.legend()

        plt.xlabel('Month')
        plt.ylabel('Avg score of products')

        path = os.path.join(self.path, 'fig', f'fig-{field}.pdf')
        plt.savefig(path)

    def aggregate_two_line2(self, data1, data2, field=None):
        data1 = np.array(data1, dtype=float)
        data2 = np.array(data2, dtype=float)

        means1 = np.mean(data1, axis=0)
        means2 = np.mean(data2, axis=0)  

        months = list(range(1, len(means1) + 1))

        plt.figure(figsize=(10, 5))

        stdev1 = np.std(data1, axis=0)
        stdev2 = np.std(data2, axis=0)
        
        background_start1 = means1 - stdev1
        background_end1 = means1 + stdev1
        background_start2 = means2 - stdev2
        background_end2 = means2 + stdev2
        
        
        plt.fill_between(months, background_start1, background_end1, color=colors[0], alpha=0.3)
        plt.fill_between(months, background_start2, background_end2, color=colors[2], alpha=0.3)  
        plt.plot(months, means1, color=colors[0], linewidth=2, label='R1')
        plt.plot(months, means2, color=colors[2], linewidth=2, label='R2')

        plt.legend()

        plt.xlabel('Month')
        plt.ylabel(field)
        
        path = os.path.join(self.path, 'fig', f'fig-{field}.pdf')
        plt.savefig(path)
        
    def customer_flow_and_score(self, data1, data2, data3, data4):
        plt.figure()

        months = list(range(1, len(data1) + 1))
        plt.xticks(months)

        plt.plot(months, data1, label='R1', marker='o', linestyle='-', color=colors[0])
        plt.plot(months, data2, label='R2', marker='x', linestyle='--', color=colors[2])

        ax2 = plt.gca().twinx()

        ax2.plot(months, data3, label='Score1', marker='s', linestyle='-', color=colors[0])
        ax2.plot(months, data4, label='Score2', marker='^', linestyle='--', color=colors[2])

        ax2_ticks = [x for x in months if x % 2 == 0]
        ax2.set_xticks(ax2_ticks)
        ax2.set_xticklabels([])  
        ax2.set_ylabel('Scores')
        ax2.set_ylim(1, 10)
        
        lines, labels = plt.gca().get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        plt.legend(lines + lines2, labels + labels2, loc='upper left')

        plt.xlabel('Month')
        plt.ylabel('Customer')

        path = os.path.join(self.path, 'fig', 'fig-customer-flow.pdf')
        plt.savefig(path)