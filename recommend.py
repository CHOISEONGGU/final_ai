from sklearn.metrics.pairwise import cosine_similarity
from haversin import calculate_distance
from flask import Flask, request, jsonify
import numpy as np
import pandas as pd
import json
from flask import Response



df = pd.read_csv('./레스토랑.csv', encoding='utf-8')
cafe_df = pd.read_csv('./카페.csv', encoding='utf-8')
movie_df = pd.read_csv('./영화관.csv', encoding='utf-8')
park_df = pd.read_csv('./산책.csv', encoding='utf-8')
theme_df = pd.read_csv('./테마.csv', encoding='utf-8')

def recommend_restaurants(user_preferences, category, user_location, n_recommendations=5):
    # 사용자 선호도를 데이터 프레임에 추가
    user_df = pd.DataFrame(user_preferences, index=['user'])

    # 사용자가 선택한 카테고리의 레스토랑만 필터링
    filtered_data = df[df['업태구분명'] == category]

    # 데이터 프레임에 있는 모든 레스토랑과 사용자 간의 코사인 유사도 계산
    cosine_similarities = cosine_similarity(filtered_data.drop(
        ['소재지전체주소', '사업장명', '업태구분명', 'review', 'review_cleaned', 'total_sentiment', 'latitude', 'longitude',
         'keyword_sentiment'], axis=1), user_df)
    similarities_df = pd.DataFrame(cosine_similarities, columns=['similarity'], index=filtered_data.index)

    # 사용자 위치와 각 음식점 사이의 거리 계산
    distances = np.array([
        calculate_distance(user_location[0], user_location[1], lat, lon)
        for lat, lon in zip(filtered_data['latitude'], filtered_data['longitude'])
    ])

    # 거리를 역수로 변환하여 가까운 곳에 더 높은 값을 주기
    distance_scores = 1 / (1 + distances)

    # 유사도와 거리 점수를 조합 (예: 유사도 70%, 거리 점수 30%)
    combined_scores = 0.7 * similarities_df['similarity'] + 0.3 * distance_scores

    # 유사도와 거리 점수를 조합한 점수로 정렬
    recommendations = filtered_data.assign(score=combined_scores).sort_values(by='score', ascending=False)

    # 사용자와 가장 유사한 n개의 레스토랑 반환 전, 원치 않는 컬럼 제거
    recommendations = recommendations.drop(columns=['review', 'review_cleaned', 'keyword_sentiment', 'score']).head(
        n_recommendations)

    return recommendations

def recommend_cafe(user_preferences, category,user_location, n_recommendations=5):
    # 사용자 선호도를 데이터 프레임에 추가
    user_df = pd.DataFrame(user_preferences, index=['user'])

    # 사용자가 선택한 카테고리의 레스토랑만 필터링
    filtered_data = df[df['업태구분명'] == category]

    # 데이터 프레임에 있는 모든 레스토랑과 사용자 간의 코사인 유사도 계산
    cosine_similarities = cosine_similarity(filtered_data.drop(
        ['소재지전체주소', '사업장명', '업태구분명', 'review', 'review_cleaned', 'total_sentiment', 'latitude', 'longitude',
         'keyword_sentiment'], axis=1), user_df)
    similarities_df = pd.DataFrame(cosine_similarities, columns=['similarity'], index=filtered_data.index)

    # 사용자 위치와 각 음식점 사이의 거리 계산
    distances = np.array([
        calculate_distance(user_location[0], user_location[1], lat, lon)
        for lat, lon in zip(cafe_df['latitude'], cafe_df['longitude'])
    ])

    # 거리를 역수로 변환하여 가까운 곳에 더 높은 값을 주기
    distance_scores = 1 / (1 + distances)

    # 유사도와 거리 점수를 조합 (예: 유사도 70%, 거리 점수 30%)
    combined_scores = 0.8 * user_preferences['분위기'] + 0.2 * distance_scores

    # 유사도와 거리 점수를 조합한 점수로 정렬
    recommendations = cafe_df.assign(score=combined_scores).sort_values(by='score', ascending=False)

    # 사용자와 가장 유사한 n개의 레스토랑 반환 전, 원치 않는 컬럼 제거
    recommendations = recommendations.drop(columns=['review', 'review_cleaned', 'keyword_sentiment', 'score']).head(
        n_recommendations)

    return recommendations

def recommend_theme(user_location, n_recommendations=5):
    # 사용자 위치와 각 음식점 사이의 거리 계산
    distances = np.array([
        calculate_distance(user_location[0], user_location[1], lat, lon)
        for lat, lon in zip(theme_df['latitude'], theme_df['longitude'])
    ])

    # 거리를 역수로 변환하여 가까운 곳에 더 높은 값을 주기
    distance_scores = 1 / (1 + distances)

    # 유사도와 거리 점수를 조합 (예: 유사도 70%, 거리 점수 30%)
    combined_scores = 0.4 * theme_df['재미'] + 0.4 * theme_df['분위기'] + 0.2 * distance_scores

    # 유사도와 거리 점수를 조합한 점수로 정렬
    recommendations = theme_df.assign(score=combined_scores).sort_values(by='score', ascending=False)

    # 사용자와 가장 유사한 n개의 레스토랑 반환 전, 원치 않는 컬럼 제거
    recommendations = recommendations.drop(columns=['review', 'review_cleaned', 'keyword_sentiment', 'score']).head(
        n_recommendations)

    return recommendations

def recommend_optimal(user_location, n_recommendations=5):
    # 사용자 위치와 각 음식점 사이의 거리 계산 (하버사인 공식 사용)
    distances = []
    for index, row in df.iterrows():
        distance = calculate_distance(
            user_location[0], user_location[1], row['latitude'], row['longitude']
        )
        distances.append(distance)

    # 거리를 역수로 변환하여 가까운 곳에 더 높은 값을 주기
    distance_scores = 1 / (1 + np.array(distances))

    # 거리 점수를 기반으로 음식점을 추천하는 코드와 동일한 방식으로 추천 계산
    combined_scores = distance_scores
    recommendations = df.assign(score=combined_scores).sort_values(by='score', ascending=False)
    recommendations = recommendations.drop(columns=['review', 'review_cleaned', 'keyword_sentiment', 'score']).head(n_recommendations)

    return recommendations

def recommend_optimal_cafe(user_location, n_recommendations=5):
    distances = []
    for index, row in cafe_df.iterrows():
        distance = calculate_distance(
            user_location[0], user_location[1], row['latitude'], row['longitude']
        )
        distances.append(distance)

    # 거리를 역수로 변환하여 가까운 곳에 더 높은 값을 주기
    distance_scores = 1 / (1 + np.array(distances))

    # 거리 점수를 기반으로 음식점을 추천하는 코드와 동일한 방식으로 추천 계산
    combined_scores = distance_scores
    recommendations = cafe_df.assign(score=combined_scores).sort_values(by='score', ascending=False)
    recommendations = recommendations.drop(columns=['review', 'review_cleaned', 'keyword_sentiment', 'score']).head(n_recommendations)

    return recommendations

def recommend_optimal_movie(user_location, n_recommendations=5):

    distances = []
    for index, row in movie_df.iterrows():
        distance = calculate_distance(
            user_location[0], user_location[1], row['latitude'], row['longitude']
        )
        distances.append(distance)

    distance_scores = 1 / (1 + np.array(distances))

    combined_scores = distance_scores

    recommendations = movie_df.assign(score=combined_scores).sort_values(by='score', ascending=False)
    recommendations = recommendations.drop(columns=['score']).head(n_recommendations)

    return recommendations

def recommend_optimal_park(user_location, n_recommendations=5):
    distances = []
    for index, row in park_df.iterrows():
        distance = calculate_distance(
            user_location[0], user_location[1], row['latitude'], row['longitude']
        )
        distances.append(distance)

    distance_scores = 1 / (1 + np.array(distances))

    combined_scores = distance_scores

    recommendations = park_df.assign(score=combined_scores).sort_values(by='score', ascending=False)
    recommendations = recommendations.drop(columns=['score']).head(n_recommendations)

    return recommendations
