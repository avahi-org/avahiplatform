import avahiplatform
# You can configure you want
# avahiplatform.configure(iam_arn_for_medical_scribing="IAM role arn", input_bucket_name_for_medical_scribing="bucket name")
avahiplatform.configure(default_model_name='amazon.titan-embed-image-v1')


# avahiplatform.initialize_observability(metrics_file='./metrics.jsonl', start_prometheus=True, prometheus_port=8007)
# avahiplatform.summarize.create_url()

# # chatbot = avahiplatform.chatbot
# # chatbot.launch_chat_ui()
# chatbot = avahiplatform.chatbot
# chatbot.initialize_system(system_prompt="You are a Python developer. You only answer queries related to Python. If you receive any other queries, please respond with 'I don't know.'")

# # Chat with the chatbot
# response = chatbot.chat(user_input="Create me a function to add 2 numbers")
# print(f"Chatbot Response: {response["response_text"]}")


# Generate URL for csv_query
# avahiplatform.query_csv.create_url()
# csv_files = {
#     "df1": "./Test/df1.csv",
#     "df2": "./Test/df2.csv"
# }
# # In the `csv_files` dictionary, you can pass any number of CSV files 1 or more than 1, but they must follow the structure where the key is the name and the value is the path(s3_path or local_path).
# csv_query_answer = avahiplatform.query_csv("How many entries are there in df1?",
#                                            csv_file_paths=csv_files)
# print(f"csv query answer: {csv_query_answer['response_text']}")

# try:
#     output = avahiplatform.summarize_document(
#         document_path='./Test/df1.csv'
#     )
#     print(f"output: {output['response_text']}")
# except Exception as e:
#     print(f"Error occurred: {str(e)}")

# try:
#     output = avahiplatform.summarize_s3_document(
#         s3_path='s3://bucket-name/summarize.docx'
#     )
#     print(f"output: {output['response_text']}")
# except Exception as e:
#     print(f"Error occurred: {str(e)}")

# try:
#     output = avahiplatform.summarize_image(
#         image_path='./Test/041_400NB_Ramp_to_Glenridge_Conn_2024-09-13T17-30-20.340+00-00.jpg'
#     )
#     print(f"output: {output['response_text']}")
# except Exception as e:
#     print(f"Error occurred: {str(e)}")

# try:
#     output = avahiplatform.summarize_video(
#         video_path="./Test/bird_video.mp4", system_prompt="summarize the video"
#     )
#     print(f"output: {output['response_text']}")
# except Exception as e:
#     print(f"Error occurred: {str(e)}")

# article= """"**Apple Camp returns with free sessions for kids aged 6 to 10 years old**
# *By Rich Demuro*
# *(KTLA) -- Apple Camp is back in session, offering free workshops at Apple stores across the country. The theme this year: Exploring new worlds and telling stories inspired by kindness.*
# *""It taught me how to do stuff that I never knew how to do,"" said Grace Kinsera, an Apple Creative Pro.*
# *The free, 90-minute sessions are designed for children ages 6 to 10 years old. They're held throughout the summer.*
# *This particular session focuses on using the iPad to create an interactive storybook.*
# *""They're creating animations, they're adding AR shapes, 3D shapes, taking AR photos where they place the 3D shapes in the world around them,"" said Kinsera.*
# *Kids learn new skills on familiar devices, and sometimes parents do too.*
# *""I'm watching some stuff now that I was like, 'I didn't know that my iPad could do that,'"" said Mili Patel, a parent.*
# *There are bigger lessons as well.*
# *The apple company is located in California and Mumbai and Pune.*
# *""There's always room for more kindness, and to get these kids thinking about it in a thoughtful, creative way early on is wonderful,"" said Kinsera.*
# *Apple Camp is part of a larger initiative called Today at Apple, which offers free, hands-on sessions that teach valuable skills and hidden tricks.*
# *""We all want our kids to learn about technology, but in a safe way. This is a great opportunity for them to do that,"" said Patel.*
# *Sign-up is open now. Sessions run through the end of July. All campers get a free T-shirt, too!*
# *My name is John and my mail id is johnwick009@gmail.com*. I live in 132, My Street, Kingston, New York 12401, America. My phone number is 98989898987. And my Social security number is AAA-GG-SSSS.
# *To sign up, visit apple.com/today.*
# *Copyright 2023 Nexstar Media Inc. All rights reserved. This material may not be published, broadcast, rewritten, or redistributed.*"
# """
# try:
#     output = avahiplatform.structuredExtraction(input_content="s3://bucet-name/Patient’s clinical history.txt"
#     )
#     print(f"output: {output['response_text']}")
# except Exception as e:
#     print(f"Error occurred: {str(e)}")
# try:
#     output = avahiplatform.mask_data(input_content="s3://bucet-name/Patient’s clinical history.txt"
#     )
#     print(f"output: {output['response_text']}")
# except Exception as e:
#     print(f"Error occurred: {str(e)}")
# try:
#     output = avahiplatform.grammar_assistant(input_content="I in am english speaker and I like write a sentence english in. "
#     )
#     print(f"output: {output['response_text']}")
# except Exception as e:
#     print(f"Error occurred: {str(e)}")
# try:
#     output = avahiplatform.product_description_assistant("SKU123", "Summer Sale", "Young Adults"
#     )
#     print(f"output: {output['response_text']}")
# except Exception as e:
#     print(f"Error occurred: {str(e)}")
# try:
#     output = avahiplatform.generate_icdcode(input_content="s3://bucet-name/Patient’s clinical history.txt"
#     )
#     print(f"output: {output}")
# except Exception as e:
#     print(f"Error occurred: {str(e)}")

# try:
#     output = avahiplatform.medicalscribing(audio_filepath="./Test/Doctor-patient-cost-of-care-conversation-from-ec2-deployed-api.mp3"
#     )
#     print(f"output: {output}")
# except Exception as e:
#     print(f"Error occurred: {str(e)}")

# try:
#     system_prompt = 'Describe the following video, what is happening? Describe it in detail'

#     output = avahiplatform.summarize_video(
#         video_path="./Test/bird_video.mp4", system_prompt=system_prompt
#     )
#     print(f"output: {output['response_text']}")
# except Exception as e:
#     print(f"Error occurred: {str(e)}")
# from PIL import Image
# try:
#     image_prompt = 'A cat wearing the Glass and standing in the snow'

#     output = avahiplatform.generate_image(
#         image_prompt=image_prompt
#     )
#     output[0].save('./Test/output.png')
#     print(f"output: {output[1]}")
# except Exception as e:
#     print(f"Error occurred: {str(e)}")

# try:
#     # image = Image.open('./Test/041_400NB_Ramp_to_Glenridge_Conn_2024-09-13T17-30-20.340+00-00.jpg')
#     output = avahiplatform.get_similar_images("./Test/041_400NB_Ramp_to_Glenridge_Conn_2024-09-13T17-30-20.340+00-00.jpg", other_file='./Test/output.png')
#     print(f"output: {output}")
# except Exception as e:
#     print(f"Error occurred: {str(e)}")