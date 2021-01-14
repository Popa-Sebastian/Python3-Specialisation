
punctuation_chars = ["'", '"', ",", ".", "!", ":", ";", '#', '@']

def strip_punctuation(input_str):
    stripped = ""
    for c in input_str:
        if c not in punctuation_chars:
            stripped += c
    return stripped

def get_neg(input_str):
    # get rid of all punctuation marks
    stripped_input = strip_punctuation(input_str)
    # make lower-case
    stripped_input = stripped_input.lower()
    # convert to list
    stripped_input_list = stripped_input.split()

    neg_word_count = 0
    for word in stripped_input_list:
        if word in negative_words:
            neg_word_count += 1
    return neg_word_count

def get_pos(input_str):
    # get rid of all punctuation marks
    stripped_input = strip_punctuation(input_str)
    # make lower-case
    stripped_input = stripped_input.lower()
    # convert to list
    stripped_input_list = stripped_input.split()

    pos_word_count = 0
    for word in stripped_input_list:
        if word in positive_words:
            pos_word_count += 1
    return pos_word_count

def get_line_data(input_str):
    str_list = input_str.split(",")
    tweet_text = str_list[0]
    retweet_count = int(str_list[1])
    reply_count = int(str_list[2])
    return (tweet_text, retweet_count, reply_count)

def test_print(text, poss, negs, nets):
    print("text:", text)
    print("positive_score:", poss)
    print("negative_score:", negs)
    print("net score:", nets)

# lists of words to use
positive_words = []
with open("positive_words.txt") as pos_f:
    for lin in pos_f:
        if lin[0] != ';' and lin[0] != '\n':
            positive_words.append(lin.strip())


negative_words = []
with open("negative_words.txt") as pos_f:
    for lin in pos_f:
        if lin[0] != ';' and lin[0] != '\n':
            negative_words.append(lin.strip())

# open file for reading
file_read = open("project_twitter_data.csv", "r")
read_header = file_read.readline()

# open file for writing
file_write = open("resulting_data.csv", "w")
write_header = 'Number of Retweets, Number of Replies, Positive Score, Negative Score, Net Score\n'
file_write.write(write_header) # writes header to csv file

lines = file_read.readlines()
for line in lines:
    (tweet_text, retweet_count, reply_count) = get_line_data(line)
    pos_score = get_pos(tweet_text)
    neg_score = get_neg(tweet_text)
    net_score = pos_score - neg_score
    test_print(tweet_text, pos_score, neg_score, net_score)
    line_to_write = '{}, {}, {}, {}, {}\n'.format(retweet_count, reply_count, pos_score, neg_score, net_score)
    print(line_to_write)
    file_write.write(line_to_write)

# close opened files
file_read.close()
file_write.close()
