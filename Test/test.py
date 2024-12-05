import sys
import os
# Add the parent directory of logicsdk to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import avahiplatform
avahiplatform.initialize_observability(metrics_file='./metrics.jsonl', start_prometheus=True, prometheus_port=8007)
# avahiplatform.summarize.create_url()
#
# chatbot = avahiplatform.chatbot()
# chatbot.create_url()
csv_files = {
    "df1": "./StudentPerformanceFactors.csv"
}
# In the `csv_files` dictionary, you can pass any number of CSV files 1 or more than 1, but they must follow the structure where the key is the name and the value is the path(s3_path or local_path).
csv_query_answer = avahiplatform.query_csv(
    "What is the average of the attendance for each combination of values of both Parental Involvement and Access to Resources?",
    csv_file_paths=csv_files)
csv_query_answer = avahiplatform.query_csv(
    "what is the student performance when student has attended less school?",
    csv_file_paths=csv_files)
# print(f"My function was called {csv_query_answer.count} times.")
#
#
# # Generate URL for csv_query
# avahiplatform.query_csv.create_url()
summarize = avahiplatform.summarize("./summarize.pdf")
summarize_2 = avahiplatform.summarize("./summarize.docx")