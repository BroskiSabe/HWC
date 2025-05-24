# Hot Wheels Database App

This is a complete beginner-friendly web application for managing a collection of Hot Wheels cars. It features user authentication, car entry management, image uploading, filtering, search, a favorites system, and a persistent dark/light mode toggle.

## ✨ Features
- User Registration & Login
- Add/Edit/Delete cars
- Image Uploads for each car
- Filter and Search by name and category
- Light/Dark mode toggle (remembers your choice)
- Favorites system with top 5 favorites across all users
- SQLite backend with Flask

## 📁 Folder Structure
```
hotwheels_db_complete/
│
├── app.py                    # Main application logic
├── database/                 # Contains SQLite DB file (auto-created)
├── static/uploads/           # Stores uploaded car images
├── templates/                # HTML templates for frontend
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   └── edit.html
└── README.txt                # This file
```

## 🚀 Getting Started

### 1. Install Python dependencies
```
pip install flask flask-login
```

### 2. Run the app
```
python app.py
```

### 3. Open in browser
Visit `http://127.0.0.1:5000/` to start using the app.

## 🔐 Default Behavior
- You must register a new account first via `/register`.
- After logging in, you can add, view, edit, and delete cars in your collection.
- You can mark favorites and see the top 5 favorites across users.

## 📝 Notes
- All data is stored in a local SQLite database.
- Uploaded images are saved in the `static/uploads/` folder.
- Light/dark mode preference is saved using `localStorage`.

---

Created with ❤️ using Flask.
