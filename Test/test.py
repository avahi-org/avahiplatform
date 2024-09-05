import avahiai

# summarization_output = avahiai.summarize("./summarize.txt")
summarization_output = avahiai.summarize("s3://avahi-python-package-data/summarize.txt")
print(summarization_output[0])
