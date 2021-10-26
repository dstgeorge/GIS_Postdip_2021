stations <- weathercan::stations_search(coords = c(47.6212, -52.7424),
                                        dist = 1200,
                                        interval = 'daily')

write.csv(stations,
          "C:\\Data\\GS2410\\GS2410L7_StGeorge\\Tabular\\stationlist.csv",
          row.names = TRUE)


