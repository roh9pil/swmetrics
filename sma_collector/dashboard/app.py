import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine

from sma_collector.config import settings

# Dash 앱 초기화
app = dash.Dash(__name__)
app.title = "Software Metrics Dashboard"

# 데이터베이스 연결
engine = create_engine(settings.DATABASE_URL)

def load_data():
    """데이터베이스에서 데이터를 로드하여 Pandas DataFrame으로 변환합니다."""
    commits_df = pd.read_sql_table('commits', engine, parse_dates=['authored_datetime'])
    issues_df = pd.read_sql_table('issues', engine, parse_dates=['created', 'updated', 'resolved'])
    return commits_df, issues_df

# 앱 레이아웃 정의
app.layout = html.Div(children=[
    html.H1(children='소프트웨어 개발 지표 대시보드', style={'textAlign': 'center'}),

    html.Div(id='live-update-text'),
    dcc.Interval(
        id='interval-component',
        interval=60*1000, # 60초마다 업데이트
        n_intervals=0
    ),

    html.H2(children='커밋 활동'),
    dcc.Graph(id='commits-over-time-graph'),

    html.H2(children='작업자별 커밋 수'),
    dcc.Graph(id='commits-by-author-graph'),
    
    html.H2(children='이슈 상태 분포'),
    dcc.Graph(id='issue-status-pie-chart'),
])

# 콜백 함수: 인터벌에 따라 그래프 업데이트
@app.callback(
    [Output('commits-over-time-graph', 'figure'),
     Output('commits-by-author-graph', 'figure'),
     Output('issue-status-pie-chart', 'figure'),
     Output('live-update-text', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    # 데이터 다시 로드
    commits_df, issues_df = load_data()

    # 1. 시간에 따른 커밋 수 그래프
    commits_df['commit_date'] = commits_df['authored_datetime'].dt.to_period('W').dt.start_time
    commits_per_week = commits_df.groupby('commit_date').size().reset_index(name='count')
    fig_commits_time = px.bar(commits_per_week, x='commit_date', y='count', title='주별 커밋 수')

    # 2. 작업자별 커밋 수 그래프
    commits_by_author = commits_df['author_name'].value_counts().nlargest(15).reset_index()
    commits_by_author.columns = ['author_name', 'commit_count']
    fig_commits_author = px.bar(commits_by_author, x='author_name', y='commit_count', title='상위 15명 작업자별 커밋 수')

    # 3. 이슈 상태 파이 차트
    issue_status_counts = issues_df['status'].value_counts().reset_index()
    issue_status_counts.columns = ['status', 'count']
    fig_issue_status = px.pie(issue_status_counts, values='count', names='status', title='Jira 이슈 상태 분포')

    update_time = f"마지막 업데이트: {pd.Timestamp.now()}"
    
    return fig_commits_time, fig_commits_author, fig_issue_status, update_time


def run_dashboard():
    """대시보드 서버를 실행합니다."""
    app.run_server(debug=True)

if __name__ == '__main__':
    run_dashboard()

