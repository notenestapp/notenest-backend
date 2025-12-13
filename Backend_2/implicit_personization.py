#import csv
import pandas as pd


#Instead of it to be computing for everyday, be computing for the total text offered, total video offered and total consumed for 7days or 30 days
#Do we compute the score and send in a text to video affinity score every time a user is uploads a note that is to be regenerated or what


#Gets the data in a specific 'column_name' in a specific 'filename'
def get_data_pandas(filename, column_name):
    df = pd.read_csv(filename)
    if column_name in df.columns:
        return df[column_name].tolist()
    else:
        return []

#Compute the affinity score
def getting_affinity(offered_minutes, actual_minutes):
    affinity_list = []#A list of the affinity scores

    for offered, minutes in zip(offered_minutes, actual_minutes):
        affinity = minutes/offered
 
        affinity_list.append(affinity)
    return affinity_list
        #print(f"Affinity: {affinity:.2f}")#When uploading it to the user csv, upload to 2 decimal places maybe

def main():
    #Get the amount of minutes of text and video was offered from the session content csv
    text_offered_minutes = get_data_pandas('session_content.csv', 'text_offered_minutes')
    video_offered_minutes = get_data_pandas('session_content.csv', 'video_offered_minutes')
    #Here when we've regenerated a note, we'll get the word count, and maybe through youtube api, we'll get the time of the video(s) and total it then use it to get an affinity

    #Get the amount of time was spent consuming content from the engagements csv.
    text_minutes = get_data_pandas('engagements.csv', 'text_minutes')
    video_minutes = get_data_pandas('engagements.csv', 'video_minutes')
    #This is the user's data Dean will be tracking and sending to the backend

    print("issue1")#Debugging

    #The affinity scores for video and text
    text_affinity = getting_affinity(text_offered_minutes, text_minutes)
    video_affinity = getting_affinity(video_offered_minutes, video_minutes)

    print("issue2")#Debugging

    print(f"Text affinity \n{text_affinity}")
    print(f'Video affinity\n{video_affinity}')

    print("issue3")#Debugging

    #We dont need these if-else because it will be compared with was is in the user profile and then update it. Its the updated verssion that will be compared.
    #I want to compare each set of video affinity to text affinity and get the output
    for one_text_affinity, one_video_affinity in zip(text_affinity, video_affinity):
        if  one_text_affinity > one_video_affinity:
            print(f"User prefers text content: text affinity score is higher at {one_text_affinity:.2f}")
        elif one_text_affinity < one_video_affinity:
            print(f"User prefers video content: video affinity score is higher at {one_video_affinity:.2f}")
        else:
            print(one_video_affinity, one_text_affinity)

    current_text_session_score = get_data_pandas('user_profile.csv', 'text_affinity')
    current_video_session_score = get_data_pandas('user_profile.csv', 'video_affinity')

    for each in current_text_session_score:
        alpha = 0.3
        print(f"The previous affinity score is {each}")
        new_affinity_score = alpha * one_text_affinity + (1-alpha) * each

        print(f"New affinity score: {new_affinity_score}")

    #Now we will upload the data to the user_profile csv file and the for each previous content consumed, this is 
    #(Done this)will be evaluated and then compared to the previous one and updated in the csv, then this will be sent to the LLM 
    #to prioritize video or text content in note generation.


if __name__ == "__main__":
    main()