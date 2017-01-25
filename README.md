# django-movies-data
This project is using django framework, line-bot python sdk and deployed with Heroku. The functions of this project are the same with movies-data.

### How do I get set up? ###
* Make LINE@ Account with Messaging API enabled
> [LINE Business Center](https://business.line.me/en/)

* Register your Webhook URL
	1. Open [LINE Developer](https://developers.line.me/)
	2. Choose your channel
	3. Edit "Basic Information"

* Add `app_properties.py` file in *py_movies_bot* directory, and fill it with your channel secret and channel access token, like the following:

	```python
channel_secret = <your_channel_secret>
channel_access_token = <your_access_token>
	```

* Reply user's message

	```python
	line_bot_api = LineBotApi(channel_access_token)
    try:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=text_message))
    except LineBotApiError as e:
        print('Exception is raised')
	```

* Push image to user

	```python
	line_bot_api = LineBotApi(channel_access_token)
    try:
        line_bot_api.push_message(target_id, ImageSendMessage(original_content_url=poster_url,
                                                              preview_image_url=poster_url))
    except LineBotApiError as e:
        print('Exception is raised')
	```

* Construct carousel template message

	```python
	carousel_template = CarouselTemplate(columns=[
                                CarouselColumn(thumbnail_image_url=poster_url, title=title, text='Select one for more info', actions=[
                                        MessageTemplateAction(label='Full Data', text='Title \"'+title+'\"'),
                                        MessageTemplateAction(label='Summary', text='Plot \"'+title+'\"'),
                                        MessageTemplateAction(label='Poster', text='Poster \"'+title+'\"')
                                        ]),
                                CarouselColumn(thumbnail_image_url=poster_url, title=title, text='Select one for more info', actions=[
                                        MessageTemplateAction(label='Released Date', text='Released \"'+title+'\"'),
                                        MessageTemplateAction(label='Actors', text='Actors \"'+title+'\"'),
                                        MessageTemplateAction(label='Awards', text='Awards \"'+title+'\"')
                                        ])
                                ])
    template_message = TemplateSendMessage(alt_text='Your search result', template=carousel_template)
	```

* Leave group or room

	```python
	line_bot_api = LineBotApi(channel_access_token)
    try:
        if source_type == 'room':
            line_bot_api.leave_room(target_id)
        elif source_type == 'group':
            line_bot_api.leave_group(target_id)
    except LineBotApiError as e:
        print('Exception is raised')
	```

* Compile

`python manage.py runserver`

* Add requirements.txt by run this script in terminal

`pip freeze > requirements.txt`

* Add this inside Procfile

`web: gunicorn <your_project_name>.wsgi --log-file -` 

* Add to Git Repositories

`git add .`

* Commit changes

`git commit -m "Your Messages"`

* Deploy

`git push heroku master`

* Run Server

`$ heroku ps:scale web=1`

* Open logs

`heroku logs --tail`


### How do I contribute? ###

* Add your name and e-mail address into CONTRIBUTORS.txt