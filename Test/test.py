import sys
import os
# Add the parent directory of logicsdk to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import avahiplatform
# You can configure you want
# avahiplatform.configure()

avahiplatform.initialize_observability(metrics_file='./metrics.jsonl', start_prometheus=True, prometheus_port=8007)
# avahiplatform.summarize.create_url()
#
# chatbot = avahiplatform.chatbot
# chatbot.launch_chat_ui()
#
#
# # Generate URL for csv_query
# avahiplatform.query_csv.create_url()
csv_files = {
    "df1": "./Test/df1.csv",
    "df2": "./Test/df2.csv"
}
# In the `csv_files` dictionary, you can pass any number of CSV files 1 or more than 1, but they must follow the structure where the key is the name and the value is the path(s3_path or local_path).
csv_query_answer = avahiplatform.query_csv("How many entries are there in df1?",
                                           csv_file_paths=csv_files)
print(f"csv query answer: {csv_query_answer}")
