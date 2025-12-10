from utils.utils import extract_from_csv, load_to_csv
import pandas as pd
import numpy as np


def transformar_metricas(datos_in):
    print(f"Modificarmos datos entrada ... {datos_in}")
    tallas = ["XS", "S", "M", "L", "XL"]
    rating = ["A", "B", "C", "D", "E"]
    umbrales_sizes = [-1, 1000, 10000, 100000, 500000, 10000000]
    umbrales_dloc = [-1, 3, 5, 10, 20, 100]
    umbrales_coverage = [-1, 30, 50, 60, 70, 100]

    data = extract_from_csv(datos_in)

    # Empiezan las transformaciones
    data.fillna(0, inplace=True)

    # create a new column, date_parsed, with the parsed dates
    data["date_parsed"] = pd.to_datetime(data["date"], format="%Y-%m-%d %H:%M:%S")
    # get the day of the month from the date_parsed column
    data["day_of_month"] = data["date_parsed"].dt.day
    data["month_of_year"] = data["date_parsed"].dt.month
    data["year"] = data["date_parsed"].dt.year

    label_mapping = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    data["reliability_label"] = data["reliability_rating"].replace(label_mapping)
    data["sqale_label"] = data["sqale_rating"].replace(label_mapping)
    data["security_label"] = data["security_rating"].replace(label_mapping)

    data["size"] = pd.cut(x=data["ncloc"], bins=umbrales_sizes, labels=tallas)
    data["dloc_label"] = pd.cut(x=data["duplicated_lines_density"], bins=umbrales_dloc, labels=rating)
    data["coverage_label"] = pd.cut(x=100 - data["coverage"], bins=umbrales_coverage, labels=rating)

    return data

def transformar_historico(historico_in):
    print(f"Modificarmos datos entrada ... {historico_in}")
    tallas = ["XS", "S", "M", "L", "XL"]
    rating = ["A", "B", "C", "D", "E"]
    umbrales_sizes = [-1, 1000, 10000, 100000, 500000, 10000000]
    umbrales_dloc = [-1, 3, 5, 10, 20, 100]
    umbrales_coverage = [-1, 30, 50, 60, 70, 100]
    
    historico = extract_from_csv(historico_in)

    # Empiezan las transformaciones
    historico.fillna(0, inplace=True)
    
    # historico["reliability_label"] = historico["reliability_rating"]
    # historico["sqale_label"] = historico["sqale_rating"]
    # historico["security_label"] = historico["security_rating"]
    # historico["reliability_label"].replace([1, 2, 3, 4, 5], rating, inplace=True)
    # historico["sqale_label"].replace([1, 2, 3, 4, 5], rating, inplace=True)
    # historico["security_label"].replace([1, 2, 3, 4, 5], rating, inplace=True)
    
    label_mapping = {1: 'A', 2: 'B', 3: 'C', 4: 'D', 5: 'E'}
    historico["reliability_label"] = historico["reliability_rating"].replace(label_mapping)
    historico["sqale_label"] = historico["sqale_rating"].replace(label_mapping)
    historico["security_label"] = historico["security_rating"].replace(label_mapping)
    
    historico["size"] = pd.cut(x=historico["ncloc"], 
                               bins=umbrales_sizes, 
                               labels=tallas)
    
    historico["dloc_label"] = pd.cut(x=historico["duplicated_lines_density"], 
                                     bins=umbrales_dloc, 
                                     labels=rating
    )
    historico["coverage_label"] = pd.cut(x=100 - historico["coverage"], 
                                         bins=umbrales_coverage, 
                                         labels=rating
    )
    return historico

# def transformar_stats(df_stats):
#     # A=0-0.05, B=0.06-0.1, C=0.11-0.20, D=0.21-0.5, E=0.51-1
#     rating = ["E", "D", "C", "B", "A"]
#     umbrales = [-1, 0.39, 0.49, 0.7, 0.9, 1]
#     df_stats["dloc_label"] = pd.cut(
#         x=(df_stats["dloc_rating"] / df_stats["repos"]), 
#         bins=umbrales, 
#         labels=rating
#     )

#     df_stats["coverage_label"] = pd.cut(
#         x=(df_stats["coverage_rating"] / df_stats["repos"]),
#         bins=umbrales,
#         labels=rating,
#     )

#     df_stats["sqale_label"] = pd.cut(
#         x=(df_stats["sqale_rating"] / df_stats["repos"]),
#         bins=umbrales,
#         labels=rating
#     )

#     df_stats["reliability_label"] = pd.cut(
#         x=(df_stats["reliability_rating"] / df_stats["repos"]),
#         bins=umbrales,
#         labels=rating,
#     )

#     df_stats["alert_status_label"] = pd.cut(
#         x=(df_stats["alert_status_ok"] / df_stats["repos"]),
#         bins=umbrales,
#         labels=rating,
#     )

#     df_stats["security_label"] = pd.cut(
#         x=(df_stats["security_rating"] / df_stats["repos"]),
#         bins=umbrales,
#         labels=rating,
#     )

#     return df_stats

def transformar_stats(df_stats):
    # A=0-0.05, B=0.06-0.1, C=0.11-0.20, D=0.21-0.5, E=0.51-1
    rating = ["E", "D", "C", "B", "A"]
    umbrales = [-1, 0.39, 0.49, 0.7, 0.9, 1]

    def calcular_label(columna, divisor="repos"):
        return pd.cut(x=(df_stats[columna] / df_stats[divisor]).replace([np.inf, -np.inf], 0), bins=umbrales, labels=rating)

    df_stats["dloc_label"] = calcular_label("dloc_rating")
    df_stats["coverage_label"] = calcular_label("coverage_rating")
    df_stats["sqale_label"] = calcular_label("sqale_rating")
    df_stats["reliability_label"] = calcular_label("reliability_rating")
    df_stats["alert_status_label"] = calcular_label("alert_status_ok")
    df_stats["security_label"] = calcular_label("security_rating")

    return df_stats