# -*- coding: utf-8 -*-


import os
import math
import PyPDF2
import docx
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
from textblob import TextBlob as tb
STOPWORDS.add("abstract")
STOPWORDS.add("introduction")
STOPWORDS.add("conclusions")
STOPWORDS.add("author")
STOPWORDS.add("university")
STOPWORDS.add("article")
STOPWORDS.add("term")
STOPWORDS.add("terms")
stopwords = set(STOPWORDS)
def tf(word, blob): #calculates tf score of words in a file
    return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist): #calculates the number of files that each word occurs in
    counter=0
    for blob in bloblist:
        if word in blob.words:
            counter=counter+1
    return counter

def idf(word, bloblist): #calculates idf score of words in a file
    return math.log10(len(bloblist) / n_containing(word, bloblist))

def tfidf(tf_val,idf_val):#calculates idf score of words in a file
    return tf_val * idf_val

def word_cloud(dictionary,filename):# plots word cloud and saves its pdf format
    wordcloud = WordCloud(
        background_color='white',
        stopwords=stopwords,
        max_words=200,
        max_font_size=40, 
        scale=3,
        random_state=1
    ).fit_words(dictionary)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig(filename+"_word_cloud.pdf")

bloblist=[]

path="C:/Users/Celal/Desktop/obje proje/klasör"
def get_filelist(path): #get whole files with extension under given path
    filelist=[]
    for filename in os.listdir(path):
        filelist.append(filename)
    return filelist
def get_filenames_without_extension(path):#get whole files without extension under given path
    filenames=[]
    for filename in os.listdir(path):
        filenames.append(os.path.splitext(filename)[0])
    return filenames
filelist=get_filelist(path)
filenames=get_filenames_without_extension(path)

#that part can read files in .txt,.pdf,.docx formats
#reading .txt
for filename in filelist:
    if filename.endswith('.txt'):
        file = open(path+"/"+filename)
        text= file.read()
#casting text to texblob. Because textblob is useful for word processing
        blob=tb(text.lower())
#each blob holds text of a file.So bloblist holds all files' text
        bloblist.append(blob)
        file.close()
#reading .pdf
    elif filename.endswith('.pdf'):
        pdf_text=""
        pdfFile = open(path+"/"+filename , 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFile)
        page_num=pdfReader.getNumPages()
        for page in range(page_num):
            pageObj = pdfReader.getPage(page)
            txt=pageObj.extractText()
            pdf_text=pdf_text+txt
        blob=tb(pdf_text.lower())
        bloblist.append(blob)
        pdfFile.close()
#reading .docx
    elif filename.endswith('.docx'):
        docx_text=""
        doc = docx.Document(path+"/"+filename)
        for para in doc.paragraphs:
            docx_text=docx_text+" "+para.text
        blob=tb(docx_text.lower())
        bloblist.append(blob)
i=0
for blob in bloblist:
    clear_blob=set(blob.words)#it prevents duplication
    tf_data=[]
    tf_data.clear()
    tfidf_data=[]
    tfidf_data.clear()
    for word in clear_blob:
        if word not in stopwords:
            tf_score=round(tf(word,blob),5)#calculates each words tf score
            idf_score=round(idf(word,bloblist),5)#calculates each words idf score
            tfidf_score=round(tfidf(tf(word,blob),idf(word,bloblist)),5)#calculates each words tfidf score
            tf_arr=[word,tf_score]
            tfidf_arr=[word,tfidf_score]
            tf_data.append(tf_arr)#appends word and its tf score to tf_data array
            tfidf_data.append(tfidf_arr)#appends word and its tfidf score to tfidf_data array
    tf_df = pd.DataFrame(tf_data,columns=['WORD','TF SCORE'])#transforms tf_data array to dataframe for ease to see data and write csv
    sorted_tf_df=tf_df.sort_values('TF SCORE',ascending=False)#sorts dataframe
    sorted_tf_df.index=range(len(sorted_tf_df))#reset indexes of sorted dataframe
    dictionary_tf={}
    a=0
    while a < len(sorted_tf_df):#trasforms dataframe to dictionary. Because word_cloud method wants dictionary as parameter
        dictionary_tf[sorted_tf_df['WORD'][a]]=sorted_tf_df['TF SCORE'][a]
        a=a+1
    word_cloud(dictionary_tf,filenames[i]+"_tf")#create word clouds and pdf files
    
    tfidf_df = pd.DataFrame(tfidf_data,columns=['WORD','TFIDF SCORE'])
    sorted_tfidf_df=tfidf_df.sort_values('TFIDF SCORE',ascending=False)
    sorted_tfidf_df.index=range(len(sorted_tfidf_df))
    dictionary_tfidf={}
    a=0
    while a < len(sorted_tfidf_df):
        dictionary_tfidf[sorted_tfidf_df['WORD'][a]]=sorted_tfidf_df['TFIDF SCORE'][a]
        a=a+1
    word_cloud(dictionary_tfidf,filenames[i]+"_tfidf")
        
    csv_file=filenames[i]+"_tfidf.csv"
    with open(csv_file, 'w',encoding='utf-8') as myfile:#writes dataframes to csv file
        sorted_tfidf_df.head(50).to_csv(myfile, sep=';', encoding='utf-8', index=False)
    csv_file2=filenames[i]+"_tf.csv"
    with open(csv_file2, 'w',encoding='utf-8') as myfile2:
        sorted_tf_df.head(50).to_csv(myfile2, sep=';', encoding='utf-8', index=False)
    i=i+1
