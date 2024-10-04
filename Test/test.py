import avahiplatform

avahiplatform.initialize_observability(metrics_file='./metrics.jsonl', start_prometheus=True)
# avahiplatform.summarize.create_url()
#
chatbot = avahiplatform.chatbot()
chatbot.create_url()
#
#
# # Generate URL for csv_query
# avahiplatform.query_csv.create_url()
