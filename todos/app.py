from flask import Flask, abort, jsonify, redirect, render_template, request, url_for;
from flask_sqlalchemy import SQLAlchemy;
from flask_migrate import Migrate;

app = Flask(__name__);
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/todoapp';
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False;

db = SQLAlchemy(app);
migrate = Migrate(db, app);
migrate.init_app(app)

class Todo(db.Model):
    __tablename__ = 'todos';
    id = db.Column(db.Integer, primary_key = True);
    description = db.Column(db.String(), nullable = False);
    completed = db.Column(db.Boolean, default=False, nullable= False);
    list_id = db.Column(db.Integer, db.ForeignKey('todolists.id'), nullable=True);

    def __repr__(self):
        return f'<Todo {self.id} {self.description}, list {self.list_id}>'

class TodoList(db.Model):
    __tablename__ = 'todolists';
    id = db.Column(db.Integer, primary_key=True);
    name = db.Column(db.String(), nullable = False);
    todos = db.relationship('Todo', backref='list', lazy=True);

    def __repr__(self):
        return f'<TodoList {self.id} {self.name}>'

db.create_all()

@app.route('/todos/create', methods=['POST'])
def create_todo():
    error = False;
    body = {};
    try:
        description = request.get_json()['description']
        list_id = request.get_json()['list_id']
        todo = Todo(description=description)
        active_list = TodoList.query.get(list_id)
        todo.list = active_list
        db.session.add(todo)
        db.session.commit()
        body['description'] = todo.description;
        body['id'] = todo.id;
        body['completed'] = todo.completed;
    except:
        error = True;
        db.session.rollback();
        print(sys.exc_info());
    finally:
        db.session.close();
    if (error == False):
        return jsonify(body)
    else:
        abort(400)

@app.route('/todos/<todo_id>/set-completed', methods=['POST'])
def set_todo_completed(todo_id):
    try:
        complete = request.get_json()['completed'];
        todo = Todo.query.get(todo_id);
        todo.completed = complete;
        db.session.commit();
    except:
        error = True;
        db.session.rollback();
        print(sys.exc_info());
    finally:
        db.session.close;
        return redirect(url_for('index'));

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
  try:
    Todo.query.filter_by(id=todo_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  return jsonify({ 'success': True })

@app.route('/lists/<list_id>')
def get_list_todos(list_id):
    return render_template('index.html', 
            lists=TodoList.query.all(),
            active_list=TodoList.query.get(list_id),
            todos=Todo.query.filter_by(list_id=list_id).order_by('id').all());

@app.route('/')
def index():
    return redirect(url_for('get_list_todos', list_id=1));


@app.route('/lists/create', methods=['POST'])
def create_list():
    body = {}
    error = False;
    try:
        name = request.get_json()['name'];
        todolist = TodoList(name = name);
        db.session.add(todolist);
        db.session.commit()
        body['id'] = todolist.id;
        body['name'] = todolist.name;
    except:
        db.session.rollback();
        error = True;
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return jsonify(body)

@app.route('/list/<list_id>/delete', methods=['DELETE'])
def delete_list(list_id):
    error = False;
    try:
        list = TodoList.query.get(list_id);
        for todos in list.todos:
            db.session.delete(todos);
        db.session.delete(list);
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close();
    if error:
        abort(500)
    else:
        return jsonify({'success' : True})

@app.route('/lists/<list_id>/set-completed', methods=['POST'])
def update_list(list_id):
    error = False
    try:
        list = TodoList.query.get(list_id);
        for todos in list.todos:
            todos.completed = True;
        db.session.commit();
    except:
        db.session.rollback();
        error = True;
    finally:
        db.session.close();
    if error:
        abort(500)
    else:
        return '', 200

