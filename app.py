from flask import Flask, request, render_template
from PIL import Image, ImageFilter
from pprint import PrettyPrinter
#from dotenv import load_dotenv
import json
import os
import random
import requests

#load_dotenv()


app = Flask(__name__)

@app.route('/')
def homepage():
    """A homepage with handy links for your convenience."""
    return render_template('home.html')

################################################################################
# COMPLIMENTS ROUTES
################################################################################

list_of_compliments = [
    'awesome',
    'beatific',
    'blithesome',
    'conscientious',
    'coruscant',
    'erudite',
    'exquisite',
    'fabulous',
    'fantastic',
    'gorgeous',
    'indubitable',
    'ineffable',
    'magnificent',
    'outstanding',
    'propitioius',
    'remarkable',
    'spectacular',
    'splendiferous',
    'stupendous',
    'super',
    'upbeat',
    'wondrous',
    'zoetic'
]

@app.route('/compliments')
def compliments():
    """Shows the user a form to get compliments."""
    return render_template('compliments_form.html')

@app.route('/compliments_results')
def compliments_results():
    """Show the user some compliments."""
    users_name = request.args.get('users_name')
    users_compliments_bool = request.args.get('wants_compliments')
    users_compliments_amount = (request.args.get('num_compliments'))
    if users_compliments_bool == 'yes':
        users_compliments_amount = int(users_compliments_amount)
        res = random.sample(list_of_compliments, (users_compliments_amount))
    elif users_compliments_bool == 'no':
        res = ""   
    context = {
        'users_name' : users_name,
        'wants_compliments' : users_compliments_bool,
        'num_compliments' : users_compliments_amount,
        'results' : res,
    }

    return render_template('compliments_results.html', **context)


################################################################################
# ANIMAL FACTS ROUTE
################################################################################

animal_to_fact = {
    'koala': 'Koala fingerprints are so close to humans\' that they could taint crime scenes.',
    'parrot': 'Parrots will selflessly help each other out.',
    'mantis shrimp': 'The mantis shrimp has the world\'s fastest punch.',
    'lion': 'Female lions do 90 percent of the hunting.',
    'narwhal': 'Narwhal tusks are really an "inside out" tooth.'
}

@app.route('/animal_facts')
def animal_facts():
    result = None
    """Show a form to choose an animal and receive facts."""
    chosen_animal = request.args.get('animal')
    # TODO: Collect the form data and save as variables
    for animal in animal_to_fact:
        if chosen_animal == animal:
            result = animal_to_fact[animal]
    context = {
       'animal' : chosen_animal,
       'facts' : animal_to_fact,
       'results' : result
       #'result' : result
        # TODO: Enter your context variables here for:
        # - the list of all animals (get from animal_to_fact)
        # - the chosen animal fact (may be None if the user hasn't filled out the form yet)
    }
    return render_template('animal_facts.html', **context)


################################################################################
# IMAGE FILTER ROUTE
################################################################################

filter_types_dict = {
    'blur': ImageFilter.BLUR,
    'contour': ImageFilter.CONTOUR,
    'detail': ImageFilter.DETAIL,
    'edge enhance': ImageFilter.EDGE_ENHANCE,
    'emboss': ImageFilter.EMBOSS,
    'sharpen': ImageFilter.SHARPEN,
    'smooth': ImageFilter.SMOOTH
}

def save_image(image, filter_type):
    """Save the image, then return the full file path of the saved image."""
    # Append the filter type at the beginning (in case the user wants to 
    # apply multiple filters to 1 image, there won't be a name conflict)
    new_file_name = f"{filter_type}-{image.filename}"
    image.filename = new_file_name

    # Construct full file path
    file_path = os.path.join(app.root_path, 'static/images', new_file_name)
    
    # Save the image
    image.save(file_path)

    return file_path


def apply_filter(file_path, filter_name):
    """Apply a Pillow filter to a saved image."""
    i = Image.open(file_path)
    i.thumbnail((500, 500))
    i = i.filter(filter_types_dict.get(filter_name))
    i.save(file_path)

@app.route('/image_filter', methods=['GET', 'POST'])
def image_filter():
    """Filter an image uploaded by the user, using the Pillow library."""

    if request.method == 'POST':
        
        # TODO: Get the user's chosen filter type (whichever one they chose in the form) and save
        # as a variable
        # HINT: remember that we're working with a POST route here so which requests function would you use?
        filter_type = request.form.get('filter_type')
        
        # Get the image file submitted by the user
        image = request.files.get('users_image')

        # TODO: call `save_image()` on the image & the user's chosen filter type, save the returned
        # value as the new file path
        file_path = save_image(image, filter_type)
        # TODO: Call `apply_filter()` on the file path & filter type
        apply_filter(file_path, filter_type)
        image_url = f'./static/images/{image.filename}'

        context = {
            # TODO: Add context variables here for:
            'filters' : filter_types_dict,
            'image_url' : image_url,
            # - The full list of filter types
            # - The image URL
        }

        return render_template('image_filter.html', **context)

    else: # if it's a GET request
        context = {
            # TODO: Add context variable here for the full list of filter types
            'filters' : filter_types_dict,
        }
        return render_template('image_filter.html', **context)


################################################################################
# GIF SEARCH ROUTE
################################################################################


API_KEY = os.getenv('API_KEY')
print(API_KEY)
TENOR_URL = 'https://tenor.googleapis.com/v2/search'
#TENOR_URL = 'https://api.tenor.com/v1/search'

pp = PrettyPrinter(indent=4)

@app.route('/gif_search', methods=['GET', 'POST'])
def gif_search():
    """Show a form to search for GIFs and show resulting GIFs from Tenor API."""
    if request.method == 'POST':
        # TODO: Get the search query & number of GIFs requested by the user, store each as a 
        # variable
        gif_choice = request.form.get('search_query')
        gif_quantity = request.form.get('quantity')
        response = requests.get(
            TENOR_URL,
            {
                # TODO: Add in key-value pairs for:
                # - 'q': the search query
                'q' : gif_choice,
                # - 'key': the API key (defined above)
                'key' : 'AIzaSyD6eboLLs7x-b8C6uiH4dSI1nrg1RbQee4',
                # - 'limit': the number of GIFs requested
                'limit' : gif_quantity,
            })
       
        gifs = json.loads(response.content).get('results')
        
        context = {
            'gifs': gifs,
        }

        # Uncomment me to see the result JSON!
        pp.pprint(gifs)

        return render_template('gif_search.html', **context)
    else:
        return render_template('gif_search.html')

if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
