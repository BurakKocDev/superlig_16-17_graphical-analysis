import json
import pandas as pd
import matplotlib.pyplot as plt

# JSON dosyasını açma
file_path = r'C:\Users\Asus\Desktop\spyder\superlig_16-17.json'
with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# İşlenmiş maç verilerini saklamak için bir liste oluştur
processed_matches = []

for week_data in data:
    week = week_data['week']
    for match in week_data['matches']:
        home_team = match['homeTeam']['name']
        away_team = match['awayTeam']['name']
        score = match['match']['score']
        home_score, away_score = map(int, score.split(' - '))
        
        processed_matches.append({
            'week': week,
            'home_team': home_team,
            'away_team': away_team,
            'home_score': home_score,
            'away_score': away_score
        })

# Verileri bir DataFrame'e dönüştür
df = pd.DataFrame(processed_matches)

# Calculate total goals scored by each team
home_goals = df.groupby('home_team')['home_score'].sum().reset_index()
away_goals = df.groupby('away_team')['away_score'].sum().reset_index()
total_goals = home_goals.merge(away_goals, left_on='home_team', right_on='away_team', how='outer')

# Ensure team names are strings
total_goals['home_team'] = total_goals['home_team'].astype(str)
total_goals['away_team'] = total_goals['away_team'].astype(str)

total_goals.fillna(0, inplace=True)
total_goals['total_goals'] = total_goals['home_score'] + total_goals['away_score']
total_goals.rename(columns={'home_team': 'team'}, inplace=True)

# Plot total goals scored by each team
plt.figure(figsize=(10, 6))
plt.barh(total_goals['team'], total_goals['total_goals'], color='skyblue')
plt.xlabel('Total Goals')
plt.title('Total Goals Scored by Each Team (2016-2017 Season)')
plt.tight_layout()
plt.show()




# Haftalık toplam gol sayısını hesapla
df['total_goals'] = df['home_score'] + df['away_score']
weekly_goals = df.groupby('week')['total_goals'].sum().reset_index()

# Haftalık toplam gol sayısını çiz
plt.figure(figsize=(10, 6))
plt.plot(weekly_goals['week'], weekly_goals['total_goals'], marker='o', color='b')
plt.xlabel('Hafta')
plt.ylabel('Toplam Gol Sayısı')
plt.title('Haftalık Toplam Gol Sayısı (2016-2017 Sezonu)')
plt.grid(True)
plt.tight_layout()
plt.show()


# Maç sonuçlarını belirleme
def get_match_result(row):
    if row['home_score'] > row['away_score']:
        return 'Home Win'
    elif row['home_score'] < row['away_score']:
        return 'Away Win'
    else:
        return 'Draw'

df['result'] = df.apply(get_match_result, axis=1)

# Sonuçların sayısını hesaplama
result_counts = df['result'].value_counts()

# Pasta grafiği çizme
plt.figure(figsize=(8, 8))
plt.pie(result_counts, labels=result_counts.index, autopct='%1.1f%%', startangle=140, colors=['#66b3ff','#99ff99','#ff9999'])
plt.title('Maç Sonuçları Dağılımı (2016-2017 Sezonu)')
plt.show()




# Ev sahibi ve deplasman takımlarının performansını hesaplama
home_performance = df['result'].value_counts()
away_performance = df['result'].apply(lambda x: 'Away Win' if x == 'Home Win' else ('Home Win' if x == 'Away Win' else x)).value_counts()

# Performansları bir DataFrame'e dönüştürme
performance_df = pd.DataFrame({
    'Home': home_performance,
    'Away': away_performance
}).fillna(0)

# Performans oranlarını hesaplama
performance_df = performance_df / len(df) * 100

# Sütun grafiği çizme
performance_df.plot(kind='bar', figsize=(10, 6), color=['#66b3ff', '#99ff99'])
plt.xlabel('Sonuç')
plt.ylabel('Yüzde (%)')
plt.title('Ev Sahibi ve Deplasman Takımlarının Performansı (2016-2017 Sezonu)')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()





# Puanları hesaplama fonksiyonu
def get_points(row, team, is_home):
    if is_home:
        if row['home_team'] == team:
            if row['home_score'] > row['away_score']:
                return 3
            elif row['home_score'] == row['away_score']:
                return 1
            else:
                return 0
        else:
            return 0
    else:
        if row['away_team'] == team:
            if row['away_score'] > row['home_score']:
                return 3
            elif row['away_score'] == row['home_score']:
                return 1
            else:
                return 0
        else:
            return 0

# Tüm takımların listesini elde etme
teams = list(set(df['home_team']).union(set(df['away_team'])))

# Her takım için haftalık performans verilerini hesaplama
team_performance = {}
for team in teams:
    weekly_points = []
    for week in sorted(df['week'].unique()):
        week_matches = df[df['week'] == week]
        points = 0
        for _, match in week_matches.iterrows():
            points += get_points(match, team, True)
            points += get_points(match, team, False)
        weekly_points.append(points)
    team_performance[team] = weekly_points

# Her takımın haftalık performansını bir DataFrame'e dönüştürme
performance_df = pd.DataFrame(team_performance, index=sorted(df['week'].unique()))

# Çizgi grafiği çizme
plt.figure(figsize=(15, 10))
for team in performance_df.columns:
    plt.plot(performance_df.index, performance_df[team], marker='o', label=team)

plt.xlabel('Hafta')
plt.ylabel('Puan')
plt.title('Takım Bazında Haftalık Performans (2016-2017 Sezonu)')
plt.legend(title='Takımlar', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True)
plt.tight_layout()
plt.show()