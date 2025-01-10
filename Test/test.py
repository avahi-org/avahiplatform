import sys
import os
# Add the parent directory of logicsdk to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import avahiplatform
avahiplatform.initialize_observability(metrics_file='./metrics.jsonl', start_prometheus=True, prometheus_port=8007)
# avahiplatform.summarize.create_url()
#
chatbot = avahiplatform.chatbot
chatbot.launch_chat_ui()
#
#
# # Generate URL for csv_query
# avahiplatform.query_csv.create_url()
