import pandas as pd
import numpy as np

from sklearn.cluster import KMeans


class KmeansSupportResistance:
    
    def __init__(self, df: pd.DataFrame, saturation_point=0.5):
        self.optimum = None

        self.wcss = []
        self.clusters = []
        self.levels = []
        
        self.df = df
        self.saturation_point = saturation_point
        
        self.__compute_kmeans_wcss()
        self.__retrieve_centroids()
        
    def __compute_kmeans_wcss(self):
        '''
        :param df: dataframe
        :param saturation_point: The amount of difference we are willing to detect
        :return: clusters with optimum K centers
        
        This method uses elbow method to find the optimum number of K clusters
        We initialize different K-means with 1..10 centers and compare the inertias
        If the difference is no more than saturation_point, we choose that as K and move on
        '''

        size = min(11, len(self.df.index))
        for i in range(1, size):
            kmeans = KMeans(n_clusters=i, init='k-means++', max_iter=300, n_init=10, random_state=0)
            kmeans.fit(self.df)
            
            self.wcss.append(kmeans.inertia_)
            self.clusters.append(kmeans)

        # Compare differences in inertias until it's no more than saturation_point
        optimum_k = len(self.wcss)-1
        for i in range(0, len(self.wcss)-1):
            delta = self.wcss[i+1] / self.wcss[i]

            if delta > self.saturation_point:
                optimum_k = i + 1
                break

        print("Optimum K is " + str(optimum_k + 1))
        self.optimum = self.clusters[optimum_k]

    def __retrieve_centroids(self):
        """ i.e. support and resistance levels. """
        self.levels = self.optimum.cluster_centers_
        self.levels = np.sort(self.levels, axis=0).reshape(-1)

# class PlotLevels():
    
#     @staticmethod
#     def plot_all(levels, df):
#         fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
        
#         candlestick_ohlc(
#             ax,df.values,
#             width=0.1*(mdates.date2num(df.index[1])-mdates.date2num(df.index[0])), 
#             colorup='green', 
#             colordown='red', 
#             alpha=0.8
#         )

#         date_format = mpl_dates.DateFormatter('%d %b %Y')
#         ax.xaxis.set_major_formatter(date_format)
#         for level in levels:
#             plt.hlines(level[1], xmin=df['Date'][level[0]], xmax=max(df['Date']), colors='blue', linestyle='--', linewidths=1)


class FractalPattern():

    def __init__(self, df):
        self.df = df
        self.levels = []
        
        self.get_levels()

    def is_support(self, i):
        cond1 = self.df['Low'][i] < self.df['Low'][i-1] 
        cond2 = self.df['Low'][i] < self.df['Low'][i+1] 
        cond3 = self.df['Low'][i+1] < self.df['Low'][i+2] 
        cond4 = self.df['Low'][i-1] < self.df['Low'][i-2]
        return (cond1 and cond2 and cond3 and cond4)

    def is_resistance(self, i):
        cond1 = self.df['High'][i] > self.df['High'][i-1] 
        cond2 = self.df['High'][i] > self.df['High'][i+1] 
        cond3 = self.df['High'][i+1] > self.df['High'][i+2] 
        cond4 = self.df['High'][i-1] > self.df['High'][i-2]
        return (cond1 and cond2 and cond3 and cond4)

    def is_far_from_level(self, value):
        average =  np.mean(self.df['High'] - self.df['Low'])
        return np.sum([abs(value - level) < average for _, level in self.levels]) == 0

    def get_levels(self):
        for i in range(2, len(self.df) - 2):

            if self.is_support(i):
                l = self.df['Low'][i]
                
                if self.is_far_from_level(l):
                    self.levels.append((i,l))
            
            elif self.is_resistance(i):
                l = self.df['High'][i]
                
                if self.is_far_from_level(l):
                    self.levels.append((i,l))
        
        return self.levels


class WindowShiftingPattern():
    def __init__(self, df):
        self.df = df
        self.levels = []
        
        self.get_levels()
    
    def is_far_from_level(self, value, levels, df):
        ave =  np.mean(df['High'] - df['Low'])
        return np.sum([abs(value - level) < ave for _, level in levels]) == 0
    
    def get_levels(self):
        pivots = []
        max_list = []
        min_list = []

        for i in range(5, len(self.df)-5):
            high_range = self.df['High'][i-5:i+4]
            current_max = high_range.max()

            if current_max not in max_list:
                max_list = []
            max_list.append(current_max)
            if len(max_list) == 5 and self.is_far_from_level(current_max, pivots, self.df):
                pivots.append((high_range.idxmax(), current_max))

            low_range = self.df['Low'][i-5:i+5]
            current_min = low_range.min()
            if current_min not in min_list:
                min_list = []
            min_list.append(current_min)
            if len(min_list) == 5 and self.is_far_from_level(current_min, pivots, self.df):
                pivots.append((low_range.idxmin(), current_min))
        
        self.levels = pivots
   