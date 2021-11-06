import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap as Basemap
import matplotlib.lines as graph_lines




def main():

    #flights data

    flights_d = pd.read_csv('flights.csv')

    #airports data
    airports_d = pd.read_csv('airports.csv')

    # selecting the columns we will be using.

    df1 = flights_d[['YEAR','MONTH'	,'DAY',	'AIRLINE','FLIGHT_NUMBER','TAIL_NUMBER','ORIGIN_AIRPORT','DESTINATION_AIRPORT','SCHEDULED_DEPARTURE'
    	,'DEPARTURE_TIME','DEPARTURE_DELAY']]

    #  Merging the 3 columns to 1

    df1['Date']= pd.to_datetime(df1[['YEAR', 'MONTH', 'DAY']])
    
    #
    df1 = df1[['Date',	'AIRLINE','FLIGHT_NUMBER','TAIL_NUMBER','ORIGIN_AIRPORT','DESTINATION_AIRPORT','SCHEDULED_DEPARTURE'
    	,'DEPARTURE_TIME','DEPARTURE_DELAY']]



    ##################################################

    # Dataframe containing routes, ORIGIN,Destination,counts ( number of flights between them)
    routes_total =  pd.DataFrame(df1.groupby(['ORIGIN_AIRPORT', 'DESTINATION_AIRPORT']).size().reset_index(name='flight_cnt'))

    # removing empty and incorrect columns , e.g only using airport with 3 letter IATA Code.
    routes_total = routes_total[routes_total.ORIGIN_AIRPORT.str.contains(r'[A-Z][A-Z][A-Z]', na=False)]

    # convert data
    routes_total.to_csv('routes_total.csv')


    flight_cnt = routes_total['ORIGIN_AIRPORT'].append(routes_total.loc[routes_total['ORIGIN_AIRPORT'] != routes_total['DESTINATION_AIRPORT'], 'DESTINATION_AIRPORT']).value_counts()
    flight_cnt = pd.DataFrame({'IATA_CODE': flight_cnt.index, 'flight-count': flight_cnt})
    flight_cnt.to_csv("flight_cnt.csv")
    pos_data = flight_cnt.merge(airports_d, on = 'IATA_CODE')


    # with weights
    graph = nx.from_pandas_edgelist(routes_total, source = 'ORIGIN_AIRPORT', target = 'DESTINATION_AIRPORT',edge_attr = 'flight_cnt',create_using = nx.DiGraph())

    # without weights
    graph_un = nx.from_pandas_edgelist(routes_total, source = 'ORIGIN_AIRPORT', target = 'DESTINATION_AIRPORT')
    

    
    
    def draw_network(graph,flight_cnt,pos_data):  
      
      plt.figure(figsize=(20,25))
    
    
      map = Basemap(projection='merc', llcrnrlon=-180,llcrnrlat=10,urcrnrlon=-50,urcrnrlat=70,lat_ts=0,resolution='l',suppress_ticks=True)
      map_long, map_lat = map(pos_data['LONGITUDE'].values, pos_data['LATITUDE'].values)
    
      nodes_position = {}
      
      for count, elem in enumerate (pos_data['IATA_CODE']):
          
          nodes_position[elem] = (map_long[count], map_lat[count])

      #print(str(nodes_position))        

      # creating nodes and edges on basemap
      nx.draw_networkx_nodes(G = graph, pos = nodes_position, nodelist = [x for x in graph.nodes() if flight_cnt['flight-count'][x] >= 100],node_color = 'r', alpha = 0.8,node_size = [flight_cnt['flight-count'][x]*3  for x in graph.nodes() if flight_cnt['flight-count'][x] >= 100])

      nx.draw_networkx_labels(G = graph, pos = nodes_position, font_size=6,font_color="white",labels = {x:x for x in graph.nodes() if flight_cnt['flight-count'][x] >= 100})

      nx.draw_networkx_nodes(G = graph, pos = nodes_position, nodelist = [x for x in graph.nodes() if flight_cnt['flight-count'][x] < 100],node_color = 'yellow', alpha = 0.6,node_size = [flight_cnt['flight-count'][x]*3  for x in graph.nodes() if flight_cnt['flight-count'][x] < 100])

      nx.draw_networkx_edges(G = graph, pos = nodes_position, edge_color='black', alpha=0.2, arrows = False)
      plt.title("Domestic Flight Network of USA", fontsize = 38)
      map.drawcountries(linewidth = 3)
      map.drawstates(linewidth = 0.3)
      map.drawcoastlines(linewidth=1.5)
      map.fillcontinents(alpha = 0.3)
      legend_elem1 = graph_lines.Line2D(range(1), range(1), color="white", marker='o', markerfacecolor="red")
      legend_elem2 = graph_lines.Line2D(range(1), range(1), color="white", marker='o',markerfacecolor="yellow")
      legend_elem3 = graph_lines.Line2D(range(1), range(1), color="black", marker='',markerfacecolor="black")
      plt.legend((legend_elem1, legend_elem2, legend_elem3), ('Airports with > 100 routes', 'Airports with < 100 routes', 'Direct route'),
                loc=4, fontsize = 'xx-large')
    
      plt.tight_layout()
      plt.savefig("flight_network.png", format = "png", dpi = 310)

    
    
    def bet_centrality(graph):

          result_dict = nx.betweenness_centrality(graph)

          bet_centrality_df = pd.DataFrame.from_dict({
          'node': list(result_dict.keys()),
          'bet_centrality': list(result_dict.values())
            })

          bet_centrality_df = bet_centrality_df.sort_values('bet_centrality', ascending=False)

          bet_centrality_df.to_csv("bet_centrality.csv")
    
    def degree_centrality(graph):

          result_dict = nx.degree_centrality(graph)

          deg_centrality_df = pd.DataFrame.from_dict({
          'node': list(result_dict.keys()),
          'deg_centrality': list(result_dict.values())
            })

          deg_centrality_df = deg_centrality_df.sort_values('deg_centrality', ascending=False)

          deg_centrality_df.to_csv("deg_centrality.csv")

    def pagerank_measure(graph):
          
          result_dict = nx.pagerank(graph)

          pagerank_df = pd.DataFrame.from_dict({
          'node': list(result_dict.keys()),
          'pagerank': list(result_dict.values())
            })

          pagerank_df = pagerank_df.sort_values('pagerank', ascending=False)

          pagerank_df.to_csv("pagerank.csv")

    
    
   
   
   
   
   
   
   
    draw_network(graph,flight_cnt,pos_data)
    bet_centrality(graph)
    degree_centrality(graph)
    pagerank_measure(graph)


if __name__ == "__main__":
    main()  