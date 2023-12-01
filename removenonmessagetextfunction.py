

def remove_non_message_text(export_text_lines):
    messages = export_text_lines[1:-1]

    filter_out_msgs = ("<Media omitted>",)
    return tuple((msg for msg in messages if msg not in filter_out_msgs))

if __name__ == "__main__":
    message_corpus = remove_chat_metadata("chat.txt")
    cleaned_corpus = remove_non_message_text(message_corpus)
    print(cleaned_corpus)