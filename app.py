import streamlit as st
import psycopg2
from dotenv import load_dotenv
import os


# Database connection
# con = psycopg2.connect(user="louisams", password="Zk901101", host="techin510-louisa.postgres.database.azure.com", database="postgres", sslmode="require")

load_dotenv()
# Connect to the Azure database
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = os.environ.get("DB_NAME")
DB_SSL = os.environ.get("DB_SSL")

con = psycopg2.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    sslmode=DB_SSL
)
cur = con.cursor()

# Function to execute SQL queries
def execute_query(query, params=None):
    with con:
        with con.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Check if the query is a SELECT query
            if query.strip().lower().startswith("select"):
                result = cursor.fetchall()
                return result
            else:
                # For non-SELECT queries, return None
                return None


# Function to create new task
def create_task(title, prompt):
    query = "INSERT INTO tasks (title, prompt, favorite) VALUES (%s, %s, %s)"
    execute_query(query, (title, prompt, False))

# Function to list all tasks
def list_tasks(show_favorite=False):
    if show_favorite:
        query = "SELECT * FROM tasks WHERE favorite = TRUE"
    else:
        query = "SELECT * FROM tasks"
    return execute_query(query)

# Function to list favorite tasks
def list_favorite_tasks():
    query = "SELECT * FROM tasks WHERE favorite = TRUE"
    return execute_query(query)

# Function to search tasks
def search_tasks(keyword):
    query = "SELECT * FROM tasks WHERE title LIKE %s OR prompt LIKE %s"
    return execute_query(query, ('%' + keyword + '%', '%' + keyword + '%'))

# Function to mark a task as favorite
def mark_as_favorite(task_id):
    query = "UPDATE tasks SET favorite = TRUE WHERE id = %s"
    execute_query(query, (task_id,))

# Function to remove a task from favorites
def remove_from_favorites(task_id):
    query = "UPDATE tasks SET favorite = FALSE WHERE id = %s"
    execute_query(query, (task_id,))
    
# Function to update a task
def update_task(task_id, title, prompt):
    query = "UPDATE tasks SET title = %s, prompt = %s WHERE id = %s"
    execute_query(query, (title, prompt, task_id))
    
# Function to delete a task
def delete_task(task_id):
    query = "DELETE FROM tasks WHERE id = %s"
    execute_query(query, (task_id,))
    
    
def main():
    st.title("Prompt Manager")

    # Add new task
    st.header("Create New Prompt ✏️")
    new_title = st.text_input("Title")
    new_prompt = st.text_area("Prompt")
    if st.button("Create"):
        create_task(new_title, new_prompt)
        st.success("Task created successfully!")
        
    # Section for updating a prompt
    st.header("Update Prompt 🔄")
    task_id_update = st.text_input("Enter Task ID to Update")
    update_title = st.text_input("New Title")
    update_prompt = st.text_area("New Prompt")
    if st.button("Update"):
        update_task(task_id_update, update_title, update_prompt)
        st.success("Task updated successfully!")


    # Layout for listing all tasks
    st.header("All Prompts 📝")
    show_favorite = st.checkbox("Show only favorite prompts")
    tasks = list_tasks(show_favorite)
    if not tasks:
        st.info("No prompts found.")
    else:
        cols = st.columns(5)
        cols[0].write("ID")
        cols[1].write("Title")
        cols[2].write("Prompt")
        cols[3].write("Favorite")
        cols[4].write("Delete")
        for row in tasks:
            cols = st.columns(5)
            cols[0].write(row[0])
            cols[1].write(row[1])
            cols[2].write(row[2])
            favorite = cols[3].checkbox("", value=row[3], key=f"favorite_checkbox_{row[0]}")

            if favorite:
                mark_as_favorite(row[0])
            else:
                remove_from_favorites(row[0])

            if cols[4].button(f"Delete {row[0]}", key=f"delete_button_{row[0]}"):
                delete_task(row[0])


    # Search tasks
    st.header("Search Prompts 🔍")
    search_term = st.text_input("Search by keyword in title")
    if st.button("Search"):
        search_results = search_tasks(search_term)
        for result in search_results:
            st.write(result)
            
    

if __name__ == "__main__":
    main()
