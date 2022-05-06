from utility.data_optimized import allUsers

p = allUsers()

p.interactions().to_csv("database_contents.csv")