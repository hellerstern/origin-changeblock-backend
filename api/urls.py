from django.urls import path
import api.views as views

urlpatterns = [
    path('health', views.HealthCheck.as_view(), name='api health check'),
    path('random-index', views.RandomIndex.as_view(), name='get random index'),
    path('get-contribution-plot', views.ContributionPlot.as_view(),
         name='get contribution plot'),
    path('get-sentiment-analysis',
         views.SentimentAnalysis.as_view(), name='get Sentiment'),
    path('get-contrib-summary', views.ContributionTable.as_view(),
         name='get contribution summary'),
    path('get-features', views.GetFeatures.as_view(), name='get features list'),
    path('get-pdp-plot', views.PartialDependencyPlot.as_view(), name='get pdp plot'),
    path('ner', views.NerSpacy.as_view(), name='get entities'),
    path('get-summary', views.Summary.as_view(), name='get summary'),
    path('get-feature-importance', views.FeatureImportance.as_view(),
         name='get feature importance'),
    path('get-pred-proba', views.GetSuccessFailureProb.as_view(),
         name='Get Success Failure Prob'),
    path('pie-chart', views.GetPieChart.as_view(), name='Get pie chart'),
    path('get-features-input', views.GetFeaturesInput.as_view(),
         name='Get features input'),
    path('get-expert-advice', views.ExpertAdvice.as_view(),
         name='Get Expert Advice'),
    # path('auth_test', views.AuthTest.as_view(), name = 'api auth check'),
    # path('signup', views.SignupView.as_view(), name = 'signup'),
    # path('login', views.LoginView.as_view(), name = 'login'),
]
