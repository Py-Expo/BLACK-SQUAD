import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import csv

class RecipeSearchApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Recipe Search")
        self.create_widgets()
        self.load_recipes_from_csv()

    def create_widgets(self):
        self.create_input_widgets()
        self.create_results_widgets()

    def create_input_widgets(self):
        input_frame = ttk.Frame(self.master)
        input_frame.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.ingredient_label = ttk.Label(input_frame, text="Enter Ingredient(s):")
        self.ingredient_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.ingredient_entry = ttk.Entry(input_frame)
        self.ingredient_entry.grid(row=0, column=1, padx=5, pady=5)

        self.search_button = ttk.Button(input_frame, text="Search", command=self.search)
        self.search_button.grid(row=0, column=2, padx=5, pady=5)

        self.clear_button = ttk.Button(input_frame, text="Clear", command=self.clear_results)
        self.clear_button.grid(row=0, column=3, padx=5, pady=5)

    def create_results_widgets(self):
        results_frame = ttk.Frame(self.master)
        results_frame.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)

        self.result_list = tk.Listbox(results_frame)
        self.result_list.grid(row=0, column=0, padx=5, pady=5, sticky=tk.NSEW)
        self.result_list.bind('<<ListboxSelect>>', self.display_recipe)

        self.recipe_text = tk.Text(results_frame, wrap=tk.WORD)
        self.recipe_text.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)

        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)

    def load_recipes_from_csv(self):
        csv_file = 'recipes.csv'
        self.recipes = {}
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                recipe_name = row['Recipe']
                ingredients = row['Ingredients'].split(',')
                instructions = row['Instructions']
                self.recipes[recipe_name] = {'ingredients': ingredients, 'instructions': instructions}

    def search(self):
        user_input = self.ingredient_entry.get()
        ingredients = [ingredient.strip().lower() for ingredient in user_input.split(',')]
        matching_recipes = self.recommend_recipe(ingredients)
        self.display_search_results(matching_recipes)

    def recommend_recipe(self, query):
        matching_recipes = {}
        for recipe_name, recipe_details in self.recipes.items():
            if all(ingredient in [ing.lower() for ing in recipe_details["ingredients"]] for ingredient in query):
                matching_recipes[recipe_name] = recipe_details
        return matching_recipes

    def display_search_results(self, matching_recipes):
        self.result_list.delete(0, tk.END)
        if matching_recipes:
            for recipe_name in sorted(matching_recipes.keys()):
                self.result_list.insert(tk.END, recipe_name)
        else:
            messagebox.showinfo("No Results", f"No recipes found containing '{self.ingredient_entry.get()}'. Please try a different ingredient.")

    def display_recipe(self, event):
        selected_index = self.result_list.curselection()
        if selected_index:
            selected_recipe = self.result_list.get(selected_index)
            recipe_details = self.recipes[selected_recipe]
            ingredients = ", ".join(recipe_details['ingredients'])
            instructions = recipe_details['instructions']
            self.recipe_text.delete(1.0, tk.END)
            self.recipe_text.insert(tk.END, f"Ingredients:\n{ingredients}\n\nInstructions:\n{instructions}")

            # Scroll down to the recipe text
            self.master.update_idletasks()
            self.recipe_text.see(tk.END)

    def clear_results(self):
        self.ingredient_entry.delete(0, tk.END)
        self.result_list.delete(0, tk.END)
        self.recipe_text.delete(1.0, tk.END)

class LoginPage:
    def __init__(self, master):
        self.master = master
        self.master.title("Login")
        self.create_widgets()

    def create_widgets(self):
        login_frame = ttk.Frame(self.master)
        login_frame.grid(row=0, column=0, padx=100, pady=50)

        self.username_label = ttk.Label(login_frame, text="Username:")
        self.username_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = ttk.Label(login_frame, text="Password:")
        self.password_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = ttk.Button(login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.E)

        self.signup_button = ttk.Button(login_frame, text="Sign Up", command=self.signup)
        self.signup_button.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check if the username and password match in the database
        if self.validate_user(username, password):
            self.open_recipe_search_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def validate_user(self, username, password):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        return user is not None

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check if the username already exists in the database
        if self.username_exists(username):
            messagebox.showerror("Sign Up Failed", "Username already exists")
        else:
            # Insert the new user into the database
            self.insert_user(username, password)
            messagebox.showinfo("Sign Up Successful", "Account created successfully. You can now login.")

            # Open RecipeSearchApp after successful signup
            self.open_recipe_search_app()

    def username_exists(self, username):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        return user is not None

    def insert_user(self, username, password):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

    def open_recipe_search_app(self):
        self.master.destroy()
        root = tk.Tk()
        app = RecipeSearchApp(root)
        root.mainloop()

def main():
    create_database()  # Create the database first
    root = tk.Tk()
    app = LoginPage(root)
    root.mainloop()

def create_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 username TEXT UNIQUE, 
                 password TEXT)''')
    conn.commit()
    conn.close()



    def recommend_recipe(self, query):
        matching_recipes = {}
        for recipe_name, recipe_details in self.recipes.items():
            if all(ingredient in [ing.lower() for ing in recipe_details["ingredients"]] for ingredient in query):
                matching_recipes[recipe_name] = recipe_details
        return matching_recipes

    def display_search_results(self, matching_recipes):
        self.result_list.delete(0, tk.END)
        if matching_recipes:
            for recipe_name in sorted(matching_recipes.keys()):
                self.result_list.insert(tk.END, recipe_name)
        else:
            messagebox.showinfo("No Results", f"No recipes found containing '{self.ingredient_entry.get()}'. Please try a different ingredient.")

    def display_recipe(self, event):
        selected_index = self.result_list.curselection()
        if selected_index:
            selected_recipe = self.result_list.get(selected_index)
            recipe_details = self.recipes[selected_recipe]
            ingredients = ", ".join(recipe_details['ingredients'])
            instructions = recipe_details['instructions']
            self.recipe_text.delete(1.0, tk.END)
            self.recipe_text.insert(tk.END, f"Ingredients:\n{ingredients}\n\nInstructions:\n{instructions}")

            # Scroll down to the recipe text
            self.master.update_idletasks()
            self.recipe_text.see(tk.END)

    def clear_results(self):
        self.ingredient_entry.delete(0, tk.END)
        self.result_list.delete(0, tk.END)
        self.recipe_text.delete(1.0, tk.END)

class LoginPage:
    def __init__(self, master):
        self.master = master
        self.master.title("Login")
        self.create_widgets()

    def create_widgets(self):
        login_frame = ttk.Frame(self.master)
        login_frame.grid(row=0, column=0, padx=100, pady=50)

        self.username_label = ttk.Label(login_frame, text="Username:")
        self.username_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)

        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        self.password_label = ttk.Label(login_frame, text="Password:")
        self.password_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)

        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        self.login_button = ttk.Button(login_frame, text="Login", command=self.login)
        self.login_button.grid(row=2, column=1, padx=5, pady=5, sticky=tk.E)

        self.signup_button = ttk.Button(login_frame, text="Sign Up", command=self.signup)
        self.signup_button.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check if the username and password match in the database
        if self.validate_user(username, password):
            self.open_recipe_search_app()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")

    def validate_user(self, username, password):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        return user is not None

    def signup(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Check if the username already exists in the database
        if self.username_exists(username):
            messagebox.showerror("Sign Up Failed", "Username already exists")
        else:
            # Insert the new user into the database
            self.insert_user(username, password)
            messagebox.showinfo("Sign Up Successful", "Account created successfully. You can now login.")

            # Open RecipeSearchApp after successful signup
            self.open_recipe_search_app()

    def username_exists(self, username):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        return user is not None

    def insert_user(self, username, password):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()

    def open_recipe_search_app(self):
        self.master.destroy()
        root = tk.Tk()
        app = RecipeSearchApp(root)
        root.mainloop()

def main():
    create_database()  # Create the database first
    root = tk.Tk()
    app = LoginPage(root)
    root.mainloop()

def create_database():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 username TEXT UNIQUE, 
                 password TEXT)''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()