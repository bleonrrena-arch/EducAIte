Welcome to EducAIte, an educational app which leverages the capabilities of AI to generate lectures and quizzes designed to make learning more accessible and engaging for students.

Before launching the app, make sure to set up your API key in the keys.env file. Just replace ApiKeyGoesHere with your valid Google Gemini API key. A multi-key fallback mechanism was used during development to ensure reliability. If you would also like to use multiple keys, place them in the format GEMINI_API_KEY_N=ApiKeyGoesHere where N is the next number in the sequence. 

When launching, either double-click on the app.py file or use the this command in the Windows Command Prompt: python app.py. Then navigate to the address that is shown in the terminal (eg.: http://127.0.0.1:5000). From here, feel free to either explore the app on your own or follow the guide below.

At the main page you are presented with two buttons that navigate are used to navigate to the Lecture and Quiz Generation pages respectively. After checking out the main page you can either use those buttons or the collapsible sidebar that is accessed by clicking the minimized square icon of the app at the top left of each page. After clicking the Services tab, you can select between the two previous pages.

On the Lecture Generation page users can put in a text prompt which will be used to generate a full lecture with an introduction, body, conclusion, and a quiz. After studying the lecture the user can test themselves on the quiz which provides immediate client-side validation. If the user wishes to, they can also click the "Save Lecture" button to store the lecture in the local database and access it later.

The Quiz Generation page is dedicated to quizzes using either a text or file input which contains the lecture contents. Once finished with it, users can continuously generate more unique quizzes.

Finally, by opening the sidebar the user can view their stored lectures, and choose to either delete or view them in a separate page. 
