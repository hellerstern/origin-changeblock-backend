from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import pandas as pd
import time
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from MyExplainer.Explainer import ClassifierExplainer
from .utils import *
from Sentiment.tweet_analysis import *
from NER.extract_text import extract_text
from NER.extract_entities import extract_entities_spacy
from Summary_helper.summary_func import summary, summarize
from Feat_Importance.scaling import scaling_func
import os
import openai


openai.api_key = "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"

config = {
    "apiKey": "AIzaSyA7arfYOAJUIak7PWMlZTVJ0vbIq8Au5Jk",
    "authDomain": "changeblock-c3897.firebaseapp.com",
    "databaseURL": "",
    "storageBucket":  "changeblock-c3897.appspot.com",
    "messagingSenderId": "321929154495"
}

# Read CSV
df = pd.read_csv('MyExplainer/cbdata.csv', index_col=0)
df = df.reset_index(drop='index')
# splitting the data
X = df.drop(columns=['Prob_of_Success'])
y = df['Prob_of_Success']
# using traintest split to generate training and testing data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=50)

# Generating the XAI Dashboard
model = RandomForestClassifier(
    n_estimators=2, max_depth=2).fit(X_train, y_train)
explainer = ClassifierExplainer(model, X_test, y_test)


class HealthCheck(APIView):
    def get(self, request):
        return Response({"message": "Server is up and running!"}, status=status.HTTP_200_OK)


class RandomIndex(APIView):
    def get(self, request):
        index = explainer.random_index()
        return Response({"index": index}, status.HTTP_200_OK)


class GetSuccessFailureProb(APIView):
    def post(self, request):
        if "index" in request.data:
            x = explainer.prediction_result_df(index=request.data["index"])
            return Response({"prediction": x}, status.HTTP_200_OK)
        elif "features" in request.data:
            data = pd.DataFrame(request.data["features"])
            x = explainer.prediction_result_df(X_row=data)
            return Response({"prediction": x}, status.HTTP_200_OK)
        else:
            Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            index = request.data["index"]
        except Exception as e:
            Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetPieChart(APIView):
    def post(self, request):
        if "index" in request.data:
            x = explainer.plot_prediction_result(index=request.data["index"])
            result = fig(x)
            return Response({"chart": result}, status.HTTP_200_OK)
        elif "features" in request.data:
            data = pd.DataFrame(request.data["features"])
            x = explainer.plot_prediction_result(X_row=data)
            result = fig(x)
            return Response({"chart": result}, status.HTTP_200_OK)
        else:
            Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ContributionPlot(APIView):
    def post(self, request):
        if "index" in request.data:
            x = explainer.plot_contributions(index=request.data["index"])
            result = fig(x)
            return Response({"message": "contribution plot", "html": result}, status=status.HTTP_200_OK)
        elif "features" in request.data:
            data = pd.DataFrame(request.data["features"])
            x = explainer.plot_contributions(X_row=data)
            result = fig(x)
            return Response({"message": "contribution plot", "html": result}, status=status.HTTP_200_OK)
        else:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SentimentAnalysis(APIView):
    def post(self, request):
        countries_list = None
        hash_tags = None
        try:
            countries_list = request.data["countries"]
            hash_tags = request.data["hashtags"]
        except Exception as e:
            Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        tweets_df = listings(countries_list, hash_tags, 3)
        _, score = analysis(tweets_df)
        if score >= 2.5:
            label = "Negative"
        else:
            label = "Positive"

        return Response({"score": score, "label": label}, status=status.HTTP_200_OK)


class ContributionTable(APIView):
    def post(self, request):
        if "index" in request.data:
            x = explainer.get_contrib_summary_df(index=request.data["index"])
            return Response({"message": "contribution summary", "data": x}, status=status.HTTP_200_OK)
        elif "features" in request.data:
            data = pd.DataFrame(request.data["features"])
            x = explainer.get_contrib_summary_df(X_row=data)
            return Response({"message": "contribution summary", "data": x}, status=status.HTTP_200_OK)
        else:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetFeatures(APIView):
    def get(self, request):
        # x = explainer.columns
        x = explainer.get_X_row()
        y = {
            "Methodology": "How the accreditation methodology followed by a project impacts its risk exposure.",
            "Project Description": "The overall description of the carbon project.",
            "Country": "The country in which the project is located.",
            "Capital_Cost": "The cost of the capital required for the project.",
            "LONG_FCST": "The predicted long-term outcome of the project.",
            "Region": "The specific region in which the project is located.",
            "Project_life": "The estimated duration of the project.",
            "Start_Year": "The year in which the project started.",
            "CAPACITY": "The capacity of the project.",
            "COST": "The cost of the project.",
            "LOC_ID": "A unique identifier for the project's location.",
            "PRICE": "The price of the project.",
            "PROD_ID": "A unique identifier for the project's product.",
            "SIZE": "The size of the project.",
            "MARGIN": "The profit margin of the project.",
            "TIER": "A classification for the project."
        }
        return Response({"message": "Features List", "features": x, "features_description": y}, status=status.HTTP_200_OK)


class GetFeaturesInput(APIView):
    def post(self, request):
        try:
            index = request.data["index"]
        except Exception as e:
            Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        x = explainer.get_X_row(index=index)
        y = {
            "Methodology": "How the accreditation methodology followed by a project impacts its risk exposure.",
            "Project Description": "The overall description of the carbon project.",
            "Country": "The country in which the project is located.",
            "Capital Cost": "The cost of the capital required for the project.",
            "Long-term Forecast": "The predicted long-term outcome of the project.",
            "Region": "The specific region in which the project is located.",
            "Project Life": "The estimated duration of the project.",
            "Start Year": "The year in which the project started.",
            "Capacity": "The capacity of the project.",
            "Cost": "The cost of the project.",
            "Location ID": "A unique identifier for the project's location.",
            "Price": "The price of the project.",
            "Product ID": "A unique identifier for the project's product.",
            "Size": "The size of the project.",
            "Margin": "The profit margin of the project.",
            "Tier": "A classification for the project."
        }
        return Response({"message": "Features List", "features": x, "features_description": y}, status=status.HTTP_200_OK)

# class GetPrediction(APIView):
#     def post(self, request):
#         try:
#             index = request.data["index"]
#         except Exception as e:
#             Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         return Response({"message": "Features List", "features": x}, status=status.HTTP_200_OK)


class PartialDependencyPlot(APIView):
    def post(self, request):
        try:
            index = request.data["index"]
            feature = request.data["feature"]
            sample = request.data["sample"]
            gridpoints = request.data["gridpoints"]
            gridlines = request.data["gridlines"]
        except Exception as e:
            Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        x = explainer.plot_pdp(index=index, col=feature, sample=sample,
                               gridpoints=gridpoints, gridlines=gridlines)
        result = fig(x)

        return Response({"message": "PDP plot", "html": result}, status=status.HTTP_200_OK)


class NerSpacy(APIView):
    def post(self, request):
        file = request.FILES["file"]
        # for filename, file in request.FILES.items():
        # return Response({"message": "File received", "filename": file.content_type})
        file_path = "file_ner_" + str(time.time())
        if not file:
            return {"message": "No file sent"}
        else:
            # check if file is docx
            if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                file_path += ".docx"
                with open(file_path, "wb") as f:
                    file_data = file.read()
                    f.write(file_data)
            # check if file is doc
            elif file.content_type == "application/msword":
                file_path += ".doc"
                with open(file_path, "wb") as f:
                    file_data = file.read()
                    f.write(file_data)
            # check if file is pdf
            elif file.content_type == "application/pdf":
                file_path += ".pdf"
                with open(file_path, "wb") as f:
                    file_data = file.read()
                    f.write(file_data)
            text = extract_text(file_path)
            entities = extract_entities_spacy(text)

            # remove file
            os.remove(file_path)
            return Response({
                "text": text,
                "entities": entities,
                "status": "success",
                "file_size": file.size,
                "extensions": file.content_type
            })


class Summary(APIView):
    def post(self, request):
        file = request.FILES["file"]
        # for filename, file in request.FILES.items():
        # return Response({"message": "File received", "filename": file.content_type})
        file_path = "file_ner_" + str(time.time())
        if not file:
            return {"message": "No file sent"}
        else:
            # check if file is docx
            if file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                file_path += ".docx"
                with open(file_path, "wb") as f:
                    file_data = file.read()
                    f.write(file_data)
            # check if file is doc
            elif file.content_type == "application/msword":
                file_path += ".doc"
                with open(file_path, "wb") as f:
                    file_data = file.read()
                    f.write(file_data)
            # check if file is pdf
            elif file.content_type == "application/pdf":
                file_path += ".pdf"
                with open(file_path, "wb") as f:
                    file_data = file.read()
                    f.write(file_data)
            text = extract_text(file_path)
            summed = summarize(text)
            os.remove(file_path)
            return Response({"text": summed})


class FeatureImportance(APIView):
    def post(self, request):
        api_in = request.data
        success_results = float(api_in['success']) * 100
        failure_results = float(api_in['failure']) * 100

        # api_in = scaling_func(api_in)
        api_in = api_in["features"]

        final_output = "Features Explanation:\n"

        prompt = f"""
        You are a world class climate expert. Use the provided details to generate content based of the feature list, probabilties and results.

        The success percentage is {success_results}% and the failure rate is {failure_results}%.
        Features List:
        Methodology- {api_in['Methodology']} - Range is 0-1
        Project life- {api_in['Project_life']} - Range is 10433817-10110001
        Project description- {api_in['Project Description']} - Range is 0-160
        Capital cost- {api_in['Capital_Cost']} - Range is 0-1
        Long-FCST- {api_in['LONG_FCST']} - Range is 0-404.11
        Tier- {api_in['TIER']} - Range is 1-2
        Region- {api_in['Region']} - Range is 0-165
        Cost- {api_in['COST']} - Range is 0-2000
        Capacity- {api_in['CAPACITY']} - Range is 193-10000
        Price- {api_in['PRICE']} - Range is 0-2800
        Size- {api_in['SIZE']} - Range is 0-1
        Margin- {api_in['MARGIN']} - Range is -200-330

        You must not not show these values and the ranges! 
        Based on the given features and the likelihood of project success or failure, provide a detailed explanation of the outcome:

        """
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=512,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0)

        final_output += response.choices[0].text
        return Response({'feature_explanation': final_output})


class ExpertAdvice(APIView):
    def post(self, request):
        data = request.data["feature_explanation"]

        prompt = data + "\nYou are a world class climate expert. Provide expert advice based on the features and the likelly outcome on how the client can improve their chances of project success: \n"

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=512,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0)

        # final_output += f"\n\nExpert Advise: \n {response.choices[0].text}"

        return Response({"expert_advise": response.choices[0].text})
