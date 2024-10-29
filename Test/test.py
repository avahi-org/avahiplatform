import avahiplatform
bedrock_helpers, s3_helpers = avahiplatform.create_helpers()

# answer = avahiplatform.summarize("./summarize.docx", bedrock_helpers, s3_helpers)
# print(answer[0])
answer = avahiplatform.structredExtraction("./summarize.docx", bedrock_helpers, s3_helpers)
print(answer[0])
