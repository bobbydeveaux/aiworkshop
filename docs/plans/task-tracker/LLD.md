# Low-Level Design: aiworkshop

**Created:** 2026-02-02T17:31:19Z
**Status:** Draft

## 1. Implementation Overview

<!-- AI: Brief summary of implementation approach -->

The task tracker application will be implemented as a three-tier monolithic architecture using:

- **Backend**: Node.js with Express.js and TypeScript, following a modular MVC pattern with separate routers, controllers, services, and repositories
- **Frontend**: React with TypeScript and Vite, using functional components with hooks, React Router for navigation, and Axios for API calls
- **Database**: PostgreSQL with Sequelize ORM for data modeling and migrations
- **Authentication**: JWT-based stateless authentication with bcrypt password hashing

The implementation follows the existing repository structure by:
- Adding new backend code to `src/api/` (expanding from the existing `main.py`)
- Creating a new `frontend/` directory at root for the React application
- Adding database migrations to `src/models/migrations/`
- Creating comprehensive tests in the root `test_*` pattern and new `tests/` directory

The development approach prioritizes:
1. Database schema and migrations first
2. Backend API implementation with authentication
3. Frontend UI components and routing
4. Integration testing across the full stack
5. Docker containerization for deployment

---

## 2. File Structure

<!-- AI: List all new and modified files with descriptions -->

```
# New Backend Files
src/
  api/
    server.ts                      # Express server initialization and configuration
    app.ts                         # Express app setup with middleware
    routes/
      index.ts                     # Route aggregation and registration
      auth.routes.ts               # Authentication endpoints (register, login, logout)
      tasks.routes.ts              # Task CRUD endpoints
    controllers/
      auth.controller.ts           # Authentication business logic handlers
      tasks.controller.ts          # Task CRUD operation handlers
    services/
      auth.service.ts              # User authentication and token management
      tasks.service.ts             # Task business logic layer
      user.service.ts              # User management operations
    repositories/
      user.repository.ts           # Database operations for users
      task.repository.ts           # Database operations for tasks
    middleware/
      auth.middleware.ts           # JWT validation and user context injection
      error.middleware.ts          # Global error handling
      validation.middleware.ts     # Request validation schemas
      rate-limit.middleware.ts     # Rate limiting configuration
    validators/
      auth.validator.ts            # Joi schemas for auth endpoints
      task.validator.ts            # Joi schemas for task endpoints
    utils/
      jwt.util.ts                  # JWT generation and verification
      password.util.ts             # Password hashing and comparison
      logger.ts                    # Winston logger configuration
      constants.ts                 # Application constants and enums
    types/
      index.ts                     # TypeScript type definitions
      express.d.ts                 # Express request augmentation
    config/
      database.config.ts           # Sequelize database configuration
      app.config.ts                # Application configuration from env
  models/
    index.ts                       # Sequelize model aggregation
    user.model.ts                  # User entity model with associations
    task.model.ts                  # Task entity model with associations
    migrations/
      001-create-users-table.ts    # Initial users table migration
      002-create-tasks-table.ts    # Initial tasks table migration
      003-add-indexes.ts           # Performance indexes migration

# New Frontend Files
frontend/
  package.json                     # Frontend dependencies
  tsconfig.json                    # TypeScript configuration
  vite.config.ts                   # Vite build configuration
  index.html                       # HTML entry point
  public/
    favicon.ico                    # Application icon
  src/
    main.tsx                       # React application entry point
    App.tsx                        # Root component with routing
    vite-env.d.ts                  # Vite type declarations
    pages/
      LoginPage.tsx                # Login form and logic
      RegisterPage.tsx             # Registration form and logic
      TasksDashboard.tsx           # Main task list view
      NotFoundPage.tsx             # 404 error page
    components/
      TaskList.tsx                 # Task list rendering component
      TaskItem.tsx                 # Individual task display
      TaskForm.tsx                 # Task create/edit form
      TaskFilter.tsx               # Status filter controls
      Header.tsx                   # Application header with logout
      PrivateRoute.tsx             # Protected route wrapper
      LoadingSpinner.tsx           # Loading state indicator
    services/
      api.service.ts               # Axios instance configuration
      auth.service.ts              # Authentication API calls
      task.service.ts              # Task CRUD API calls
    context/
      AuthContext.tsx              # Authentication state management
    hooks/
      useAuth.ts                   # Custom hook for auth context
      useTasks.ts                  # Custom hook for task operations
    types/
      index.ts                     # TypeScript interfaces
    utils/
      storage.ts                   # LocalStorage wrapper for tokens
      validators.ts                # Client-side validation utilities
    styles/
      index.css                    # Global styles with Tailwind

# Configuration Files
.env.example                       # Environment variables template
.env.development                   # Development environment config
.env.production                    # Production environment config
docker-compose.yml                 # Local development orchestration
Dockerfile.backend                 # Backend container definition
Dockerfile.frontend                # Frontend container definition
nginx.conf                         # Nginx reverse proxy configuration

# Backend Package Files
package.json                       # Backend dependencies (root)
tsconfig.json                      # TypeScript config for backend
jest.config.js                     # Jest testing configuration
.eslintrc.js                       # ESLint code quality rules
.prettierrc                        # Prettier formatting rules

# Testing Files
tests/
  unit/
    services/
      auth.service.test.ts         # Auth service unit tests
      tasks.service.test.ts        # Task service unit tests
    utils/
      jwt.util.test.ts             # JWT utility tests
      password.util.test.ts        # Password utility tests
  integration/
    auth.routes.test.ts            # Auth endpoint integration tests
    tasks.routes.test.ts           # Task endpoint integration tests
  e2e/
    user-flow.test.ts              # Full user journey E2E tests
  fixtures/
    users.fixture.ts               # Test user data
    tasks.fixture.ts               # Test task data
  helpers/
    db-setup.ts                    # Test database setup/teardown
    auth-helper.ts                 # Authentication test utilities

# Documentation Updates
docs/
  plans/
    task-tracker/
      LLD.md                       # This document
  api/
    openapi.yaml                   # OpenAPI 3.0 specification
  deployment/
    setup-guide.md                 # Deployment instructions
    docker-guide.md                # Container setup guide
README.md                          # Updated with task tracker info

# Modified Files
src/api/main.py                    # Archived or removed (replaced by server.ts)
```

---

## 3. Detailed Component Designs

<!-- AI: For each major component from HLD, provide detailed design -->

### 3.1 Backend API Server (`src/api/server.ts` and `src/api/app.ts`)

**Purpose**: Initialize Express server with middleware, routes, and error handling

**server.ts Structure**:
```typescript
import app from './app';
import { sequelize } from './config/database.config';
import logger from './utils/logger';

const PORT = process.env.PORT || 3000;

async function startServer() {
  try {
    // Test database connection
    await sequelize.authenticate();
    logger.info('Database connected successfully');
    
    // Sync models (development only)
    if (process.env.NODE_ENV === 'development') {
      await sequelize.sync({ alter: true });
    }
    
    // Start HTTP server
    app.listen(PORT, () => {
      logger.info(`Server running on port ${PORT}`);
    });
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
}

startServer();
```

**app.ts Structure**:
```typescript
import express, { Application } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import compression from 'compression';
import routes from './routes';
import { errorHandler } from './middleware/error.middleware';
import { rateLimiter } from './middleware/rate-limit.middleware';

const app: Application = express();

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
  credentials: true
}));

// Request parsing
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(compression());

// Logging
app.use(morgan('combined'));

// Rate limiting
app.use('/api', rateLimiter);

// Health check
app.get('/api/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// API routes
app.use('/api', routes);

// Error handling (must be last)
app.use(errorHandler);

export default app;
```

### 3.2 Authentication Controller (`src/api/controllers/auth.controller.ts`)

**Purpose**: Handle HTTP requests for registration, login, and logout

**Class Design**:
```typescript
import { Request, Response, NextFunction } from 'express';
import { AuthService } from '../services/auth.service';
import { AppError } from '../middleware/error.middleware';

export class AuthController {
  private authService: AuthService;

  constructor() {
    this.authService = new AuthService();
  }

  /**
   * Register a new user
   * POST /api/auth/register
   */
  register = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { email, password } = req.body;
      const result = await this.authService.register(email, password);
      
      res.status(201).json({
        message: 'User registered successfully',
        userId: result.userId
      });
    } catch (error) {
      next(error);
    }
  };

  /**
   * Login user and return JWT token
   * POST /api/auth/login
   */
  login = async (req: Request, res: Response, next: NextFunction) => {
    try {
      const { email, password } = req.body;
      const result = await this.authService.login(email, password);
      
      res.status(200).json({
        token: result.token,
        user: {
          id: result.user.id,
          email: result.user.email
        }
      });
    } catch (error) {
      next(error);
    }
  };

  /**
   * Logout user (client-side token deletion)
   * POST /api/auth/logout
   */
  logout = async (req: Request, res: Response, next: NextFunction) => {
    try {
      // For JWT, logout is primarily client-side
      // Could implement token blacklist here if needed
      res.status(200).json({
        message: 'Logged out successfully'
      });
    } catch (error) {
      next(error);
    }
  };
}
```

### 3.3 Task Management Controller (`src/api/controllers/tasks.controller.ts`)

**Purpose**: Handle HTTP requests for task CRUD operations

**Class Design**:
```typescript
import { Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
import { TasksService } from '../services/tasks.service';
import { TaskStatus } from '../utils/constants';

export class TasksController {
  private tasksService: TasksService;

  constructor() {
    this.tasksService = new TasksService();
  }

  /**
   * Get all tasks for authenticated user
   * GET /api/tasks?status=pending
   */
  getTasks = async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const userId = req.user!.id;
      const status = req.query.status as TaskStatus | undefined;
      
      const tasks = await this.tasksService.getUserTasks(userId, status);
      
      res.status(200).json({ tasks });
    } catch (error) {
      next(error);
    }
  };

  /**
   * Get single task by ID
   * GET /api/tasks/:id
   */
  getTaskById = async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const userId = req.user!.id;
      const taskId = req.params.id;
      
      const task = await this.tasksService.getTaskById(taskId, userId);
      
      res.status(200).json(task);
    } catch (error) {
      next(error);
    }
  };

  /**
   * Create new task
   * POST /api/tasks
   */
  createTask = async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const userId = req.user!.id;
      const { title, description, status } = req.body;
      
      const task = await this.tasksService.createTask({
        userId,
        title,
        description,
        status: status || TaskStatus.PENDING
      });
      
      res.status(201).json(task);
    } catch (error) {
      next(error);
    }
  };

  /**
   * Update existing task
   * PUT /api/tasks/:id
   */
  updateTask = async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const userId = req.user!.id;
      const taskId = req.params.id;
      const updates = req.body;
      
      const task = await this.tasksService.updateTask(taskId, userId, updates);
      
      res.status(200).json(task);
    } catch (error) {
      next(error);
    }
  };

  /**
   * Delete task
   * DELETE /api/tasks/:id
   */
  deleteTask = async (req: AuthRequest, res: Response, next: NextFunction) => {
    try {
      const userId = req.user!.id;
      const taskId = req.params.id;
      
      await this.tasksService.deleteTask(taskId, userId);
      
      res.status(200).json({ message: 'Task deleted successfully' });
    } catch (error) {
      next(error);
    }
  };
}
```

### 3.4 Authentication Service (`src/api/services/auth.service.ts`)

**Purpose**: Business logic for user registration, login, and token generation

**Class Design**:
```typescript
import { UserRepository } from '../repositories/user.repository';
import { hashPassword, comparePasswords } from '../utils/password.util';
import { generateToken } from '../utils/jwt.util';
import { AppError } from '../middleware/error.middleware';

export class AuthService {
  private userRepository: UserRepository;

  constructor() {
    this.userRepository = new UserRepository();
  }

  /**
   * Register new user with email and password
   * @throws AppError if email already exists or validation fails
   */
  async register(email: string, password: string): Promise<{ userId: string }> {
    // Check if user already exists
    const existingUser = await this.userRepository.findByEmail(email);
    if (existingUser) {
      throw new AppError('Email already registered', 409);
    }

    // Validate password strength (min 8 chars, complexity rules)
    this.validatePasswordStrength(password);

    // Hash password
    const passwordHash = await hashPassword(password);

    // Create user
    const user = await this.userRepository.create({
      email,
      passwordHash
    });

    return { userId: user.id };
  }

  /**
   * Authenticate user and generate JWT token
   * @throws AppError if credentials are invalid
   */
  async login(email: string, password: string): Promise<{
    token: string;
    user: { id: string; email: string };
  }> {
    // Find user by email
    const user = await this.userRepository.findByEmail(email);
    if (!user) {
      throw new AppError('Invalid credentials', 401);
    }

    // Verify password
    const isValid = await comparePasswords(password, user.passwordHash);
    if (!isValid) {
      throw new AppError('Invalid credentials', 401);
    }

    // Generate JWT token
    const token = generateToken({
      userId: user.id,
      email: user.email
    });

    return {
      token,
      user: {
        id: user.id,
        email: user.email
      }
    };
  }

  /**
   * Validate password meets strength requirements
   * @private
   */
  private validatePasswordStrength(password: string): void {
    if (password.length < 8) {
      throw new AppError('Password must be at least 8 characters', 400);
    }
    
    // Add more complexity rules as needed
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumber = /\d/.test(password);
    
    if (!hasUpperCase || !hasLowerCase || !hasNumber) {
      throw new AppError(
        'Password must contain uppercase, lowercase, and number',
        400
      );
    }
  }
}
```

### 3.5 Task Service (`src/api/services/tasks.service.ts`)

**Purpose**: Business logic for task CRUD operations with authorization

**Class Design**:
```typescript
import { TaskRepository } from '../repositories/task.repository';
import { AppError } from '../middleware/error.middleware';
import { TaskStatus } from '../utils/constants';

export interface CreateTaskDTO {
  userId: string;
  title: string;
  description?: string;
  status: TaskStatus;
}

export interface UpdateTaskDTO {
  title?: string;
  description?: string;
  status?: TaskStatus;
}

export class TasksService {
  private taskRepository: TaskRepository;

  constructor() {
    this.taskRepository = new TaskRepository();
  }

  /**
   * Get all tasks for a user, optionally filtered by status
   */
  async getUserTasks(userId: string, status?: TaskStatus) {
    return this.taskRepository.findByUserId(userId, status);
  }

  /**
   * Get single task by ID with ownership validation
   * @throws AppError if task not found or unauthorized
   */
  async getTaskById(taskId: string, userId: string) {
    const task = await this.taskRepository.findById(taskId);
    
    if (!task) {
      throw new AppError('Task not found', 404);
    }
    
    if (task.userId !== userId) {
      throw new AppError('Forbidden', 403);
    }
    
    return task;
  }

  /**
   * Create new task for user
   */
  async createTask(data: CreateTaskDTO) {
    // Validate title is not empty
    if (!data.title || data.title.trim().length === 0) {
      throw new AppError('Task title is required', 400);
    }
    
    if (data.title.length > 255) {
      throw new AppError('Task title must not exceed 255 characters', 400);
    }
    
    return this.taskRepository.create(data);
  }

  /**
   * Update existing task with ownership validation
   * @throws AppError if task not found, unauthorized, or validation fails
   */
  async updateTask(taskId: string, userId: string, updates: UpdateTaskDTO) {
    // Verify ownership
    await this.getTaskById(taskId, userId);
    
    // Validate updates
    if (updates.title !== undefined) {
      if (updates.title.trim().length === 0) {
        throw new AppError('Task title cannot be empty', 400);
      }
      if (updates.title.length > 255) {
        throw new AppError('Task title must not exceed 255 characters', 400);
      }
    }
    
    if (updates.status && !Object.values(TaskStatus).includes(updates.status)) {
      throw new AppError('Invalid task status', 400);
    }
    
    return this.taskRepository.update(taskId, updates);
  }

  /**
   * Delete task with ownership validation
   * @throws AppError if task not found or unauthorized
   */
  async deleteTask(taskId: string, userId: string) {
    // Verify ownership
    await this.getTaskById(taskId, userId);
    
    await this.taskRepository.delete(taskId);
  }
}
```

### 3.6 Authentication Middleware (`src/api/middleware/auth.middleware.ts`)

**Purpose**: Validate JWT tokens and inject user context into requests

**Implementation**:
```typescript
import { Response, NextFunction } from 'express';
import { AuthRequest } from '../types';
import { verifyToken } from '../utils/jwt.util';
import { AppError } from './error.middleware';

/**
 * Middleware to authenticate requests using JWT
 * Extracts token from Authorization header and validates it
 * Injects user data into req.user for downstream handlers
 */
export const authenticate = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    // Extract token from Authorization header
    const authHeader = req.headers.authorization;
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      throw new AppError('No token provided', 401);
    }
    
    const token = authHeader.substring(7); // Remove 'Bearer ' prefix
    
    // Verify and decode token
    const decoded = verifyToken(token);
    
    // Inject user data into request
    req.user = {
      id: decoded.userId,
      email: decoded.email
    };
    
    next();
  } catch (error) {
    if (error instanceof AppError) {
      next(error);
    } else {
      next(new AppError('Invalid or expired token', 401));
    }
  }
};
```

### 3.7 Frontend Authentication Context (`frontend/src/context/AuthContext.tsx`)

**Purpose**: Manage authentication state and provide auth methods to components

**Implementation**:
```typescript
import React, { createContext, useState, useEffect, ReactNode } from 'react';
import { authService } from '../services/auth.service';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Check for existing token on mount
  useEffect(() => {
    const token = authService.getToken();
    if (token) {
      // Decode token to get user info
      const userData = authService.getUserFromToken(token);
      setUser(userData);
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authService.login(email, password);
    setUser(response.user);
  };

  const register = async (email: string, password: string) => {
    await authService.register(email, password);
    // Auto-login after registration
    await login(email, password);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        logout,
        isAuthenticated: !!user
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
```

### 3.8 Frontend Task Dashboard (`frontend/src/pages/TasksDashboard.tsx`)

**Purpose**: Main view for displaying and managing tasks

**Component Structure**:
```typescript
import React, { useState, useEffect } from 'react';
import { TaskList } from '../components/TaskList';
import { TaskForm } from '../components/TaskForm';
import { TaskFilter } from '../components/TaskFilter';
import { Header } from '../components/Header';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useTasks } from '../hooks/useTasks';
import { Task, TaskStatus } from '../types';

export const TasksDashboard: React.FC = () => {
  const { tasks, loading, error, createTask, updateTask, deleteTask, refreshTasks } = useTasks();
  const [filter, setFilter] = useState<TaskStatus | 'all'>('all');
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  // Filter tasks based on selected status
  const filteredTasks = filter === 'all' 
    ? tasks 
    : tasks.filter(task => task.status === filter);

  const handleCreateTask = async (data: { title: string; description: string }) => {
    await createTask(data);
    setShowForm(false);
  };

  const handleUpdateTask = async (
    taskId: string, 
    updates: { title?: string; description?: string; status?: TaskStatus }
  ) => {
    await updateTask(taskId, updates);
    setEditingTask(null);
  };

  const handleDeleteTask = async (taskId: string) => {
    if (confirm('Are you sure you want to delete this task?')) {
      await deleteTask(taskId);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="dashboard">
      <Header />
      
      <div className="dashboard-content">
        <div className="dashboard-header">
          <h1>My Tasks</h1>
          <button onClick={() => setShowForm(true)} className="btn-primary">
            + New Task
          </button>
        </div>

        <TaskFilter currentFilter={filter} onFilterChange={setFilter} />

        {showForm && (
          <TaskForm
            onSubmit={handleCreateTask}
            onCancel={() => setShowForm(false)}
          />
        )}

        <TaskList
          tasks={filteredTasks}
          onEdit={setEditingTask}
          onDelete={handleDeleteTask}
          onStatusChange={(taskId, status) => handleUpdateTask(taskId, { status })}
        />
      </div>
    </div>
  );
};
```

---

## 4. Database Schema Changes

<!-- AI: SQL/migration scripts for schema changes -->

### Migration 001: Create Users Table (`src/models/migrations/001-create-users-table.ts`)

```typescript
import { QueryInterface, DataTypes } from 'sequelize';

export default {
  up: async (queryInterface: QueryInterface) => {
    await queryInterface.createTable('users', {
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
        allowNull: false
      },
      email: {
        type: DataTypes.STRING(255),
        allowNull: false,
        unique: true,
        validate: {
          isEmail: true
        }
      },
      password_hash: {
        type: DataTypes.STRING(255),
        allowNull: false
      },
      created_at: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: DataTypes.NOW
      },
      updated_at: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: DataTypes.NOW
      }
    });

    // Create unique index on email for faster lookups
    await queryInterface.addIndex('users', ['email'], {
      unique: true,
      name: 'users_email_unique_idx'
    });
  },

  down: async (queryInterface: QueryInterface) => {
    await queryInterface.dropTable('users');
  }
};
```

### Migration 002: Create Tasks Table (`src/models/migrations/002-create-tasks-table.ts`)

```typescript
import { QueryInterface, DataTypes } from 'sequelize';

export default {
  up: async (queryInterface: QueryInterface) => {
    await queryInterface.createTable('tasks', {
      id: {
        type: DataTypes.UUID,
        defaultValue: DataTypes.UUIDV4,
        primaryKey: true,
        allowNull: false
      },
      user_id: {
        type: DataTypes.UUID,
        allowNull: false,
        references: {
          model: 'users',
          key: 'id'
        },
        onUpdate: 'CASCADE',
        onDelete: 'CASCADE'
      },
      title: {
        type: DataTypes.STRING(255),
        allowNull: false,
        validate: {
          notEmpty: true,
          len: [1, 255]
        }
      },
      description: {
        type: DataTypes.TEXT,
        allowNull: true
      },
      status: {
        type: DataTypes.ENUM('pending', 'completed'),
        allowNull: false,
        defaultValue: 'pending'
      },
      created_at: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: DataTypes.NOW
      },
      updated_at: {
        type: DataTypes.DATE,
        allowNull: false,
        defaultValue: DataTypes.NOW
      }
    });
  },

  down: async (queryInterface: QueryInterface) => {
    await queryInterface.dropTable('tasks');
    // Drop the ENUM type
    await queryInterface.sequelize.query('DROP TYPE IF EXISTS "enum_tasks_status";');
  }
};
```

### Migration 003: Add Performance Indexes (`src/models/migrations/003-add-indexes.ts`)

```typescript
import { QueryInterface } from 'sequelize';

export default {
  up: async (queryInterface: QueryInterface) => {
    // Index for filtering tasks by user (most common query)
    await queryInterface.addIndex('tasks', ['user_id'], {
      name: 'tasks_user_id_idx'
    });

    // Composite index for filtering tasks by user and status
    await queryInterface.addIndex('tasks', ['user_id', 'status'], {
      name: 'tasks_user_id_status_idx'
    });

    // Index for sorting tasks by creation date
    await queryInterface.addIndex('tasks', ['created_at'], {
      name: 'tasks_created_at_idx'
    });
  },

  down: async (queryInterface: QueryInterface) => {
    await queryInterface.removeIndex('tasks', 'tasks_user_id_idx');
    await queryInterface.removeIndex('tasks', 'tasks_user_id_status_idx');
    await queryInterface.removeIndex('tasks', 'tasks_created_at_idx');
  }
};
```

### Sequelize Model: User (`src/models/user.model.ts`)

```typescript
import { Model, DataTypes, Optional } from 'sequelize';
import { sequelize } from '../api/config/database.config';

interface UserAttributes {
  id: string;
  email: string;
  passwordHash: string;
  createdAt: Date;
  updatedAt: Date;
}

interface UserCreationAttributes extends Optional<UserAttributes, 'id' | 'createdAt' | 'updatedAt'> {}

export class User extends Model<UserAttributes, UserCreationAttributes> implements UserAttributes {
  public id!: string;
  public email!: string;
  public passwordHash!: string;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

User.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true
    },
    email: {
      type: DataTypes.STRING(255),
      allowNull: false,
      unique: true,
      validate: {
        isEmail: true
      }
    },
    passwordHash: {
      type: DataTypes.STRING(255),
      allowNull: false,
      field: 'password_hash'
    },
    createdAt: {
      type: DataTypes.DATE,
      allowNull: false,
      field: 'created_at'
    },
    updatedAt: {
      type: DataTypes.DATE,
      allowNull: false,
      field: 'updated_at'
    }
  },
  {
    sequelize,
    tableName: 'users',
    timestamps: true
  }
);
```

### Sequelize Model: Task (`src/models/task.model.ts`)

```typescript
import { Model, DataTypes, Optional } from 'sequelize';
import { sequelize } from '../api/config/database.config';
import { User } from './user.model';
import { TaskStatus } from '../api/utils/constants';

interface TaskAttributes {
  id: string;
  userId: string;
  title: string;
  description?: string;
  status: TaskStatus;
  createdAt: Date;
  updatedAt: Date;
}

interface TaskCreationAttributes extends Optional<TaskAttributes, 'id' | 'description' | 'createdAt' | 'updatedAt'> {}

export class Task extends Model<TaskAttributes, TaskCreationAttributes> implements TaskAttributes {
  public id!: string;
  public userId!: string;
  public title!: string;
  public description?: string;
  public status!: TaskStatus;
  public readonly createdAt!: Date;
  public readonly updatedAt!: Date;
}

Task.init(
  {
    id: {
      type: DataTypes.UUID,
      defaultValue: DataTypes.UUIDV4,
      primaryKey: true
    },
    userId: {
      type: DataTypes.UUID,
      allowNull: false,
      field: 'user_id'
    },
    title: {
      type: DataTypes.STRING(255),
      allowNull: false,
      validate: {
        notEmpty: true,
        len: [1, 255]
      }
    },
    description: {
      type: DataTypes.TEXT,
      allowNull: true
    },
    status: {
      type: DataTypes.ENUM(...Object.values(TaskStatus)),
      allowNull: false,
      defaultValue: TaskStatus.PENDING
    },
    createdAt: {
      type: DataTypes.DATE,
      allowNull: false,
      field: 'created_at'
    },
    updatedAt: {
      type: DataTypes.DATE,
      allowNull: false,
      field: 'updated_at'
    }
  },
  {
    sequelize,
    tableName: 'tasks',
    timestamps: true
  }
);

// Define associations
User.hasMany(Task, {
  foreignKey: 'userId',
  as: 'tasks'
});

Task.belongsTo(User, {
  foreignKey: 'userId',
  as: 'user'
});
```

---

## 5. API Implementation Details

<!-- AI: For each API endpoint, specify handler logic, validation, error handling -->

### POST /api/auth/register

**Route Definition** (`src/api/routes/auth.routes.ts`):
```typescript
import { Router } from 'express';
import { AuthController } from '../controllers/auth.controller';
import { validateRequest } from '../middleware/validation.middleware';
import { registerSchema } from '../validators/auth.validator';

const router = Router();
const authController = new AuthController();

router.post('/register', validateRequest(registerSchema), authController.register);

export default router;
```

**Validation Schema** (`src/api/validators/auth.validator.ts`):
```typescript
import Joi from 'joi';

export const registerSchema = Joi.object({
  email: Joi.string().email().required().messages({
    'string.email': 'Invalid email format',
    'any.required': 'Email is required'
  }),
  password: Joi.string().min(8).pattern(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/).required().messages({
    'string.min': 'Password must be at least 8 characters',
    'string.pattern.base': 'Password must contain uppercase, lowercase, and number',
    'any.required': 'Password is required'
  })
});
```

**Request Flow**:
1. Request hits validation middleware
2. Joi schema validates email format and password strength
3. Controller calls AuthService.register()
4. Service checks for existing email in UserRepository
5. Service hashes password using bcrypt
6. Repository creates user in database
7. Controller returns 201 with userId
8. Error middleware catches and formats any errors

**Error Responses**:
- 400: Invalid email format or weak password
- 409: Email already registered
- 500: Internal server error

---

### POST /api/auth/login

**Route Definition**:
```typescript
router.post('/login', validateRequest(loginSchema), authController.login);
```

**Validation Schema**:
```typescript
export const loginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required()
});
```

**Request Flow**:
1. Validate email and password presence
2. Controller calls AuthService.login()
3. Service retrieves user by email from UserRepository
4. Service compares password hash using bcrypt
5. Service generates JWT token with user payload
6. Controller returns 200 with token and user data
7. Client stores token in localStorage

**Error Responses**:
- 400: Missing email or password
- 401: Invalid credentials (same message for wrong email or password)
- 500: Internal server error

---

### GET /api/tasks

**Route Definition** (`src/api/routes/tasks.routes.ts`):
```typescript
import { Router } from 'express';
import { TasksController } from '../controllers/tasks.controller';
import { authenticate } from '../middleware/auth.middleware';
import { validateRequest } from '../middleware/validation.middleware';
import { getTasksSchema } from '../validators/task.validator';

const router = Router();
const tasksController = new TasksController();

// All task routes require authentication
router.use(authenticate);

router.get('/', validateRequest(getTasksSchema, 'query'), tasksController.getTasks);

export default router;
```

**Validation Schema** (`src/api/validators/task.validator.ts`):
```typescript
export const getTasksSchema = Joi.object({
  status: Joi.string().valid('pending', 'completed').optional()
});
```

**Request Flow**:
1. Authentication middleware validates JWT token
2. User ID extracted from token and injected into req.user
3. Query parameter validation for optional status filter
4. Controller calls TasksService.getUserTasks()
5. Service calls TaskRepository.findByUserId()
6. Repository executes Sequelize query with user_id and optional status filter
7. Controller returns 200 with tasks array
8. Frontend displays filtered task list

**Error Responses**:
- 401: Missing or invalid token
- 400: Invalid status parameter
- 500: Internal server error

---

### POST /api/tasks

**Route Definition**:
```typescript
router.post('/', validateRequest(createTaskSchema), tasksController.createTask);
```

**Validation Schema**:
```typescript
export const createTaskSchema = Joi.object({
  title: Joi.string().min(1).max(255).required().messages({
    'string.empty': 'Task title cannot be empty',
    'string.max': 'Task title must not exceed 255 characters',
    'any.required': 'Task title is required'
  }),
  description: Joi.string().optional().allow(''),
  status: Joi.string().valid('pending', 'completed').optional().default('pending')
});
```

**Request Flow**:
1. Authentication middleware validates token
2. Request body validation against schema
3. Controller extracts userId from req.user
4. Controller calls TasksService.createTask()
5. Service validates title is not empty
6. Service calls TaskRepository.create()
7. Repository creates task in database with user_id foreign key
8. Controller returns 201 with created task object
9. Frontend adds task to local state and updates UI

**Error Responses**:
- 401: Unauthorized
- 400: Missing title, title too long, or invalid status
- 500: Internal server error

---

### PUT /api/tasks/:id

**Route Definition**:
```typescript
router.put('/:id', validateRequest(updateTaskSchema), tasksController.updateTask);
```

**Validation Schema**:
```typescript
export const updateTaskSchema = Joi.object({
  title: Joi.string().min(1).max(255).optional(),
  description: Joi.string().optional().allow(''),
  status: Joi.string().valid('pending', 'completed').optional()
}).min(1); // At least one field must be present
```

**Request Flow**:
1. Authentication middleware validates token
2. Path parameter :id extracted as taskId
3. Request body validation (at least one field required)
4. Controller calls TasksService.updateTask()
5. Service calls getTaskById() to verify task exists and belongs to user
6. Service validates update fields (title length, status enum)
7. Service calls TaskRepository.update()
8. Repository executes Sequelize update with WHERE id AND user_id
9. Controller returns 200 with updated task
10. Frontend updates task in local state

**Error Responses**:
- 401: Unauthorized
- 403: Task belongs to different user
- 404: Task not found
- 400: Invalid update data (empty title, invalid status)
- 500: Internal server error

---

### DELETE /api/tasks/:id

**Route Definition**:
```typescript
router.delete('/:id', tasksController.deleteTask);
```

**Request Flow**:
1. Authentication middleware validates token
2. Path parameter :id extracted as taskId
3. Controller calls TasksService.deleteTask()
4. Service calls getTaskById() to verify ownership
5. Service calls TaskRepository.delete()
6. Repository executes Sequelize destroy with WHERE id
7. Controller returns 200 with success message
8. Frontend removes task from local state

**Error Responses**:
- 401: Unauthorized
- 403: Task belongs to different user
- 404: Task not found
- 500: Internal server error

---

### Error Handling Middleware (`src/api/middleware/error.middleware.ts`)

```typescript
import { Request, Response, NextFunction } from 'express';
import logger from '../utils/logger';

export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number = 500,
    public isOperational: boolean = true
  ) {
    super(message);
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

export const errorHandler = (
  err: Error | AppError,
  req: Request,
  res: Response,
  next: NextFunction
) => {
  let statusCode = 500;
  let message = 'Internal server error';
  let isOperational = false;

  if (err instanceof AppError) {
    statusCode = err.statusCode;
    message = err.message;
    isOperational = err.isOperational;
  }

  // Log error
  logger.error({
    message: err.message,
    stack: err.stack,
    statusCode,
    path: req.path,
    method: req.method,
    userId: (req as any).user?.id
  });

  // Don't leak internal errors to client
  if (!isOperational) {
    message = 'Internal server error';
  }

  res.status(statusCode).json({
    error: {
      message,
      statusCode
    }
  });
};
```

---

## 6. Function Signatures

<!-- AI: Key function/method signatures with parameters and return types -->

### Authentication Utilities (`src/api/utils/jwt.util.ts`)

```typescript
import jwt from 'jsonwebtoken';
import { AppError } from '../middleware/error.middleware';

interface TokenPayload {
  userId: string;
  email: string;
}

interface DecodedToken extends TokenPayload {
  iat: number;
  exp: number;
}

/**
 * Generate JWT token for authenticated user
 * @param payload User data to encode in token
 * @param expiresIn Token expiration (default: 24h)
 * @returns Signed JWT token string
 */
export function generateToken(
  payload: TokenPayload,
  expiresIn: string = '24h'
): string {
  const secret = process.env.JWT_SECRET;
  if (!secret) {
    throw new Error('JWT_SECRET not configured');
  }

  return jwt.sign(payload, secret, { expiresIn });
}

/**
 * Verify and decode JWT token
 * @param token JWT token string
 * @returns Decoded token payload
 * @throws AppError if token is invalid or expired
 */
export function verifyToken(token: string): DecodedToken {
  const secret = process.env.JWT_SECRET;
  if (!secret) {
    throw new Error('JWT_SECRET not configured');
  }

  try {
    return jwt.verify(token, secret) as DecodedToken;
  } catch (error) {
    throw new AppError('Invalid or expired token', 401);
  }
}
```

### Password Utilities (`src/api/utils/password.util.ts`)

```typescript
import bcrypt from 'bcrypt';

const SALT_ROUNDS = 12;

/**
 * Hash password using bcrypt
 * @param password Plain text password
 * @returns Bcrypt hash string
 */
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

/**
 * Compare plain text password with hash
 * @param password Plain text password
 * @param hash Bcrypt hash to compare against
 * @returns True if password matches hash
 */
export async function comparePasswords(
  password: string,
  hash: string
): Promise<boolean> {
  return bcrypt.compare(password, hash);
}
```

### User Repository (`src/api/repositories/user.repository.ts`)

```typescript
import { User } from '../../models/user.model';

export class UserRepository {
  /**
   * Find user by email address
   * @param email Email to search for
   * @returns User model or null if not found
   */
  async findByEmail(email: string): Promise<User | null> {
    return User.findOne({ where: { email } });
  }

  /**
   * Find user by ID
   * @param id User UUID
   * @returns User model or null if not found
   */
  async findById(id: string): Promise<User | null> {
    return User.findByPk(id);
  }

  /**
   * Create new user
   * @param data User creation data
   * @returns Created user model
   */
  async create(data: { email: string; passwordHash: string }): Promise<User> {
    return User.create(data);
  }

  /**
   * Update user by ID
   * @param id User UUID
   * @param updates Fields to update
   * @returns Updated user model or null if not found
   */
  async update(id: string, updates: Partial<{ email: string; passwordHash: string }>): Promise<User | null> {
    const user = await this.findById(id);
    if (!user) return null;
    return user.update(updates);
  }

  /**
   * Delete user by ID
   * @param id User UUID
   * @returns Number of deleted rows (0 or 1)
   */
  async delete(id: string): Promise<number> {
    return User.destroy({ where: { id } });
  }
}
```

### Task Repository (`src/api/repositories/task.repository.ts`)

```typescript
import { Task } from '../../models/task.model';
import { TaskStatus } from '../utils/constants';

export class TaskRepository {
  /**
   * Find all tasks for a user, optionally filtered by status
   * @param userId User UUID
   * @param status Optional status filter
   * @returns Array of task models
   */
  async findByUserId(userId: string, status?: TaskStatus): Promise<Task[]> {
    const where: any = { userId };
    if (status) {
      where.status = status;
    }
    
    return Task.findAll({
      where,
      order: [['createdAt', 'DESC']]
    });
  }

  /**
   * Find task by ID
   * @param id Task UUID
   * @returns Task model or null if not found
   */
  async findById(id: string): Promise<Task | null> {
    return Task.findByPk(id);
  }

  /**
   * Create new task
   * @param data Task creation data
   * @returns Created task model
   */
  async create(data: {
    userId: string;
    title: string;
    description?: string;
    status: TaskStatus;
  }): Promise<Task> {
    return Task.create(data);
  }

  /**
   * Update task by ID
   * @param id Task UUID
   * @param updates Fields to update
   * @returns Updated task model or null if not found
   */
  async update(
    id: string,
    updates: Partial<{ title: string; description: string; status: TaskStatus }>
  ): Promise<Task | null> {
    const task = await this.findById(id);
    if (!task) return null;
    return task.update(updates);
  }

  /**
   * Delete task by ID
   * @param id Task UUID
   * @returns Number of deleted rows (0 or 1)
   */
  async delete(id: string): Promise<number> {
    return Task.destroy({ where: { id } });
  }
}
```

### Frontend API Service (`frontend/src/services/api.service.ts`)

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';
import { getToken, clearToken } from '../utils/storage';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000/api';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle auth errors
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Make GET request
   */
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get<T>(url, { params });
    return response.data;
  }

  /**
   * Make POST request
   */
  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<T>(url, data);
    return response.data;
  }

  /**
   * Make PUT request
   */
  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put<T>(url, data);
    return response.data;
  }

  /**
   * Make DELETE request
   */
  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<T>(url);
    return response.data;
  }
}

export const apiService = new ApiService();
```

### Frontend Task Service (`frontend/src/services/task.service.ts`)

```typescript
import { apiService } from './api.service';
import { Task, TaskStatus, CreateTaskDTO, UpdateTaskDTO } from '../types';

class TaskService {
  /**
   * Get all tasks for authenticated user
   * @param status Optional status filter
   */
  async getTasks(status?: TaskStatus): Promise<Task[]> {
    const response = await apiService.get<{ tasks: Task[] }>('/tasks', { status });
    return response.tasks;
  }

  /**
   * Get single task by ID
   */
  async getTaskById(id: string): Promise<Task> {
    return apiService.get<Task>(`/tasks/${id}`);
  }

  /**
   * Create new task
   */
  async createTask(data: CreateTaskDTO): Promise<Task> {
    return apiService.post<Task>('/tasks', data);
  }

  /**
   * Update existing task
   */
  async updateTask(id: string, data: UpdateTaskDTO): Promise<Task> {
    return apiService.put<Task>(`/tasks/${id}`, data);
  }

  /**
   * Delete task
   */
  async deleteTask(id: string): Promise<void> {
    await apiService.delete(`/tasks/${id}`);
  }
}

export const taskService = new TaskService();
```

### Frontend Custom Hook (`frontend/src/hooks/useTasks.ts`)

```typescript
import { useState, useEffect, useCallback } from 'react';
import { taskService } from '../services/task.service';
import { Task, TaskStatus, CreateTaskDTO, UpdateTaskDTO } from '../types';

interface UseTasksReturn {
  tasks: Task[];
  loading: boolean;
  error: string | null;
  createTask: (data: CreateTaskDTO) => Promise<void>;
  updateTask: (id: string, data: UpdateTaskDTO) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  refreshTasks: () => Promise<void>;
}

/**
 * Custom hook for task operations with state management
 */
export function useTasks(): UseTasksReturn {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await taskService.getTasks();
      setTasks(data);
    } catch (err: any) {
      setError(err.response?.data?.error?.message || 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks]);

  const createTask = async (data: CreateTaskDTO) => {
    try {
      const newTask = await taskService.createTask(data);
      setTasks((prev) => [newTask, ...prev]);
    } catch (err: any) {
      throw new Error(err.response?.data?.error?.message || 'Failed to create task');
    }
  };

  const updateTask = async (id: string, data: UpdateTaskDTO) => {
    try {
      const updatedTask = await taskService.updateTask(id, data);
      setTasks((prev) =>
        prev.map((task) => (task.id === id ? updatedTask : task))
      );
    } catch (err: any) {
      throw new Error(err.response?.data?.error?.message || 'Failed to update task');
    }
  };

  const deleteTask = async (id: string) => {
    try {
      await taskService.deleteTask(id);
      setTasks((prev) => prev.filter((task) => task.id !== id));
    } catch (err: any) {
      throw new Error(err.response?.data?.error?.message || 'Failed to delete task');
    }
  };

  return {
    tasks,
    loading,
    error,
    createTask,
    updateTask,
    deleteTask,
    refreshTasks: fetchTasks
  };
}
```

---

## 7. State Management

<!-- AI: How application state is managed (Redux, Context, database) -->

### Backend State Management

**Stateless Architecture**:
- No server-side session state (JWT-based authentication)
- All state stored in PostgreSQL database
- Each request is independent and self-contained
- User context derived from JWT token on each request

**Database as Source of Truth**:
- User data persisted in `users` table
- Task data persisted in `tasks` table
- Foreign key relationships enforce data integrity
- Transactions used for multi-step operations

**Connection Pooling**:
- Sequelize manages database connection pool
- Default pool size: 5 connections (configurable via environment)
- Connections reused across requests for performance
- Automatic connection release after query completion

### Frontend State Management

**React Context API for Authentication**:
```typescript
// AuthContext provides global authentication state
// State stored: user object, loading flag, authentication status
// Methods exposed: login, register, logout
// Token persisted in localStorage for session persistence
```

**Local Component State for Tasks**:
```typescript
// useTasks hook manages task list state
// State stored: tasks array, loading flag, error message
// Operations: CRUD methods that update local state and sync with backend
// No global state management library needed for MVP
```

**LocalStorage for Token Persistence**:
```typescript
// src/utils/storage.ts
const TOKEN_KEY = 'auth_token';

export const saveToken = (token: string): void => {
  localStorage.setItem(TOKEN_KEY, token);
};

export const getToken = (): string | null => {
  return localStorage.getItem(TOKEN_KEY);
};

export const clearToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
};

export const getUserFromToken = (token: string): { id: string; email: string } | null => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return { id: payload.userId, email: payload.email };
  } catch {
    return null;
  }
};
```

**State Flow**:

1. **Initial Load**:
   - App checks localStorage for token
   - If token exists, decode and set user in AuthContext
   - TasksDashboard fetches tasks from API
   - Tasks stored in component state via useTasks hook

2. **User Login**:
   - Login form submits credentials to API
   - API returns JWT token and user data
   - Token saved to localStorage
   - User object set in AuthContext
   - App redirects to dashboard
   - Dashboard loads tasks

3. **Task Operations**:
   - User creates/updates/deletes task via UI
   - API call made with JWT token
   - On success, local task state updated optimistically
   - On error, state reverted and error displayed

4. **User Logout**:
   - Logout button calls logout method
   - Token removed from localStorage
   - User cleared from AuthContext
   - App redirects to login page

**Why No Redux/MobX**:
- Simple application with limited shared state
- React Context sufficient for authentication
- Task state local to dashboard component
- Avoids boilerplate and complexity
- Can migrate to Redux if app grows in complexity

---

## 8. Error Handling Strategy

<!-- AI: Error codes, exception handling, user-facing messages -->

### Backend Error Handling

**Error Classification**:

```typescript
// src/api/utils/constants.ts
export enum ErrorCode {
  // Authentication errors (401)
  INVALID_CREDENTIALS = 'INVALID_CREDENTIALS',
  INVALID_TOKEN = 'INVALID_TOKEN',
  TOKEN_EXPIRED = 'TOKEN_EXPIRED',
  
  // Authorization errors (403)
  FORBIDDEN = 'FORBIDDEN',
  
  // Validation errors (400)
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  INVALID_INPUT = 'INVALID_INPUT',
  
  // Resource errors (404)
  NOT_FOUND = 'NOT_FOUND',
  
  // Conflict errors (409)
  DUPLICATE_EMAIL = 'DUPLICATE_EMAIL',
  
  // Server errors (500)
  INTERNAL_ERROR = 'INTERNAL_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR'
}
```

**Custom Error Class**:
```typescript
// Already defined in error.middleware.ts
export class AppError extends Error {
  constructor(
    public message: string,
    public statusCode: number = 500,
    public isOperational: boolean = true,
    public code?: ErrorCode
  ) {
    super(message);
    Object.setPrototypeOf(this, AppError.prototype);
  }
}
```

**Error Response Format**:
```json
{
  "error": {
    "message": "Human-readable error message",
    "statusCode": 400,
    "code": "VALIDATION_ERROR",
    "details": {
      "field": "email",
      "issue": "Invalid email format"
    }
  }
}
```

**Validation Error Handling**:
```typescript
// src/api/middleware/validation.middleware.ts
import { Request, Response, NextFunction } from 'express';
import { Schema } from 'joi';
import { AppError } from './error.middleware';

export const validateRequest = (schema: Schema, property: 'body' | 'query' | 'params' = 'body') => {
  return (req: Request, res: Response, next: NextFunction) => {
    const { error } = schema.validate(req[property], { abortEarly: false });
    
    if (error) {
      const details = error.details.map((detail) => ({
        field: detail.path.join('.'),
        message: detail.message
      }));
      
      const appError = new AppError('Validation error', 400, true, ErrorCode.VALIDATION_ERROR);
      (appError as any).details = details;
      
      return next(appError);
    }
    
    next();
  };
};
```

**Database Error Handling**:
```typescript
// Wrapper for repository methods
async function handleDatabaseOperation<T>(operation: () => Promise<T>): Promise<T> {
  try {
    return await operation();
  } catch (error: any) {
    // Sequelize unique constraint violation
    if (error.name === 'SequelizeUniqueConstraintError') {
      throw new AppError('Email already registered', 409, true, ErrorCode.DUPLICATE_EMAIL);
    }
    
    // Sequelize validation error
    if (error.name === 'SequelizeValidationError') {
      throw new AppError(error.errors[0].message, 400, true, ErrorCode.VALIDATION_ERROR);
    }
    
    // Foreign key constraint
    if (error.name === 'SequelizeForeignKeyConstraintError') {
      throw new AppError('Referenced resource not found', 404, true, ErrorCode.NOT_FOUND);
    }
    
    // Log unexpected database errors
    logger.error('Database error:', error);
    throw new AppError('Database operation failed', 500, false, ErrorCode.DATABASE_ERROR);
  }
}
```

**Unhandled Error Catching**:
```typescript
// src/api/server.ts
process.on('unhandledRejection', (reason: any) => {
  logger.error('Unhandled rejection:', reason);
  // In production, might want to restart process or alert
});

process.on('uncaughtException', (error: Error) => {
  logger.error('Uncaught exception:', error);
  // Graceful shutdown
  process.exit(1);
});
```

### Frontend Error Handling

**API Error Handling**:
```typescript
// frontend/src/services/api.service.ts
// Response interceptor extracts user-friendly error messages
this.client.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error: { message: string } }>) => {
    const message = error.response?.data?.error?.message || 'An error occurred';
    
    // Handle specific status codes
    if (error.response?.status === 401) {
      clearToken();
      window.location.href = '/login';
      return Promise.reject(new Error('Session expired. Please log in again.'));
    }
    
    if (error.response?.status === 403) {
      return Promise.reject(new Error('You do not have permission to perform this action'));
    }
    
    if (error.response?.status === 404) {
      return Promise.reject(new Error('Resource not found'));
    }
    
    if (error.response?.status >= 500) {
      return Promise.reject(new Error('Server error. Please try again later.'));
    }
    
    return Promise.reject(new Error(message));
  }
);
```

**Component Error Display**:
```typescript
// frontend/src/components/ErrorMessage.tsx
interface ErrorMessageProps {
  message: string;
  onDismiss?: () => void;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onDismiss }) => {
  return (
    <div className="error-banner" role="alert">
      <span className="error-icon">⚠️</span>
      <span className="error-text">{message}</span>
      {onDismiss && (
        <button onClick={onDismiss} className="error-dismiss">
          ✕
        </button>
      )}
    </div>
  );
};
```

**Form Validation Errors**:
```typescript
// frontend/src/pages/LoginPage.tsx
const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

const validate = () => {
  const newErrors: any = {};
  
  if (!email) {
    newErrors.email = 'Email is required';
  } else if (!/\S+@\S+\.\S+/.test(email)) {
    newErrors.email = 'Invalid email format';
  }
  
  if (!password) {
    newErrors.password = 'Password is required';
  } else if (password.length < 8) {
    newErrors.password = 'Password must be at least 8 characters';
  }
  
  setErrors(newErrors);
  return Object.keys(newErrors).length === 0;
};
```

**User-Facing Error Messages**:

| Error Type | Backend Message | Frontend Display |
|------------|----------------|------------------|
| Invalid email | "Invalid email format" | "Please enter a valid email address" |
| Weak password | "Password must contain uppercase, lowercase, and number" | "Password must be at least 8 characters with uppercase, lowercase, and number" |
| Duplicate email | "Email already registered" | "This email is already registered. Try logging in instead." |
| Invalid credentials | "Invalid credentials" | "Email or password is incorrect. Please try again." |
| Expired token | "Invalid or expired token" | "Your session has expired. Please log in again." |
| Task not found | "Task not found" | "This task no longer exists or has been deleted." |
| Forbidden | "Forbidden" | "You don't have permission to access this task." |
| Server error | "Internal server error" | "Something went wrong. Please try again later." |

---

## 9. Test Plan

### Unit Tests

**Backend Unit Tests**:

**Authentication Service Tests** (`tests/unit/services/auth.service.test.ts`):
```typescript
describe('AuthService', () => {
  let authService: AuthService;
  let userRepository: UserRepository;

  beforeEach(() => {
    userRepository = new UserRepository();
    authService = new AuthService();
  });

  describe('register', () => {
    it('should create new user with hashed password', async () => {
      const email = 'test@example.com';
      const password = 'SecurePass123';
      
      jest.spyOn(userRepository, 'findByEmail').mockResolvedValue(null);
      jest.spyOn(userRepository, 'create').mockResolvedValue({ id: 'uuid', email } as any);
      
      const result = await authService.register(email, password);
      
      expect(result.userId).toBe('uuid');
      expect(userRepository.create).toHaveBeenCalledWith(
        expect.objectContaining({ email })
      );
    });

    it('should throw error if email already exists', async () => {
      jest.spyOn(userRepository, 'findByEmail').mockResolvedValue({ email: 'test@example.com' } as any);
      
      await expect(authService.register('test@example.com', 'pass')).rejects.toThrow('Email already registered');
    });

    it('should throw error if password is too weak', async () => {
      await expect(authService.register('test@example.com', 'weak')).rejects.toThrow('Password must be at least 8 characters');
    });
  });

  describe('login', () => {
    it('should return token and user on valid credentials', async () => {
      const user = { id: 'uuid', email: 'test@example.com', passwordHash: 'hashed' };
      jest.spyOn(userRepository, 'findByEmail').mockResolvedValue(user as any);
      jest.spyOn(require('../utils/password.util'), 'comparePasswords').mockResolvedValue(true);
      
      const result = await authService.login('test@example.com', 'password');
      
      expect(result.token).toBeDefined();
      expect(result.user.email).toBe('test@example.com');
    });

    it('should throw error on invalid email', async () => {
      jest.spyOn(userRepository, 'findByEmail').mockResolvedValue(null);
      
      await expect(authService.login('wrong@example.com', 'pass')).rejects.toThrow('Invalid credentials');
    });

    it('should throw error on invalid password', async () => {
      jest.spyOn(userRepository, 'findByEmail').mockResolvedValue({ passwordHash: 'hashed' } as any);
      jest.spyOn(require('../utils/password.util'), 'comparePasswords').mockResolvedValue(false);
      
      await expect(authService.login('test@example.com', 'wrong')).rejects.toThrow('Invalid credentials');
    });
  });
});
```

**Task Service Tests** (`tests/unit/services/tasks.service.test.ts`):
```typescript
describe('TasksService', () => {
  let tasksService: TasksService;
  let taskRepository: TaskRepository;

  beforeEach(() => {
    taskRepository = new TaskRepository();
    tasksService = new TasksService();
  });

  describe('createTask', () => {
    it('should create task with valid data', async () => {
      const taskData = {
        userId: 'user-id',
        title: 'Test Task',
        description: 'Description',
        status: TaskStatus.PENDING
      };
      
      jest.spyOn(taskRepository, 'create').mockResolvedValue({ id: 'task-id', ...taskData } as any);
      
      const result = await tasksService.createTask(taskData);
      
      expect(result.title).toBe('Test Task');
      expect(taskRepository.create).toHaveBeenCalledWith(taskData);
    });

    it('should throw error if title is empty', async () => {
      await expect(
        tasksService.createTask({ userId: 'id', title: '', status: TaskStatus.PENDING })
      ).rejects.toThrow('Task title is required');
    });

    it('should throw error if title exceeds 255 characters', async () => {
      const longTitle = 'a'.repeat(256);
      
      await expect(
        tasksService.createTask({ userId: 'id', title: longTitle, status: TaskStatus.PENDING })
      ).rejects.toThrow('Task title must not exceed 255 characters');
    });
  });

  describe('updateTask', () => {
    it('should update task if user owns it', async () => {
      const task = { id: 'task-id', userId: 'user-id', title: 'Old' };
      jest.spyOn(taskRepository, 'findById').mockResolvedValue(task as any);
      jest.spyOn(taskRepository, 'update').mockResolvedValue({ ...task, title: 'New' } as any);
      
      const result = await tasksService.updateTask('task-id', 'user-id', { title: 'New' });
      
      expect(result.title).toBe('New');
    });

    it('should throw error if user does not own task', async () => {
      jest.spyOn(taskRepository, 'findById').mockResolvedValue({ userId: 'other-user' } as any);
      
      await expect(
        tasksService.updateTask('task-id', 'user-id', { title: 'New' })
      ).rejects.toThrow('Forbidden');
    });
  });

  describe('deleteTask', () => {
    it('should delete task if user owns it', async () => {
      jest.spyOn(taskRepository, 'findById').mockResolvedValue({ userId: 'user-id' } as any);
      jest.spyOn(taskRepository, 'delete').mockResolvedValue(1);
      
      await expect(tasksService.deleteTask('task-id', 'user-id')).resolves.not.toThrow();
    });

    it('should throw error if task not found', async () => {
      jest.spyOn(taskRepository, 'findById').mockResolvedValue(null);
      
      await expect(tasksService.deleteTask('task-id', 'user-id')).rejects.toThrow('Task not found');
    });
  });
});
```

**JWT Utility Tests** (`tests/unit/utils/jwt.util.test.ts`):
```typescript
describe('JWT Utilities', () => {
  describe('generateToken', () => {
    it('should generate valid JWT token', () => {
      const payload = { userId: 'uuid', email: 'test@example.com' };
      const token = generateToken(payload);
      
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token.split('.')).toHaveLength(3);
    });
  });

  describe('verifyToken', () => {
    it('should verify and decode valid token', () => {
      const payload = { userId: 'uuid', email: 'test@example.com' };
      const token = generateToken(payload);
      
      const decoded = verifyToken(token);
      
      expect(decoded.userId).toBe('uuid');
      expect(decoded.email).toBe('test@example.com');
    });

    it('should throw error on invalid token', () => {
      expect(() => verifyToken('invalid.token.here')).toThrow('Invalid or expired token');
    });

    it('should throw error on expired token', () => {
      const token = generateToken({ userId: 'uuid', email: 'test@example.com' }, '0s');
      
      setTimeout(() => {
        expect(() => verifyToken(token)).toThrow('Invalid or expired token');
      }, 100);
    });
  });
});
```

**Frontend Unit Tests**:

**Auth Service Tests** (`frontend/src/services/__tests__/auth.service.test.ts`):
```typescript
import { authService } from '../auth.service';
import { apiService } from '../api.service';

jest.mock('../api.service');

describe('AuthService', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should save token after successful login', async () => {
    const mockResponse = { token: 'jwt-token', user: { id: '1', email: 'test@example.com' } };
    (apiService.post as jest.Mock).mockResolvedValue(mockResponse);
    
    const result = await authService.login('test@example.com', 'password');
    
    expect(result.token).toBe('jwt-token');
    expect(localStorage.getItem('auth_token')).toBe('jwt-token');
  });

  it('should clear token on logout', () => {
    localStorage.setItem('auth_token', 'jwt-token');
    
    authService.logout();
    
    expect(localStorage.getItem('auth_token')).toBeNull();
  });
});
```

**useTasks Hook Tests** (`frontend/src/hooks/__tests__/useTasks.test.ts`):
```typescript
import { renderHook, act, waitFor } from '@testing-library/react';
import { useTasks } from '../useTasks';
import { taskService } from '../../services/task.service';

jest.mock('../../services/task.service');

describe('useTasks', () => {
  it('should fetch tasks on mount', async () => {
    const mockTasks = [{ id: '1', title: 'Test Task', status: 'pending' }];
    (taskService.getTasks as jest.Mock).mockResolvedValue(mockTasks);
    
    const { result } = renderHook(() => useTasks());
    
    await waitFor(() => expect(result.current.loading).toBe(false));
    
    expect(result.current.tasks).toEqual(mockTasks);
  });

  it('should add task to list on create', async () => {
    (taskService.getTasks as jest.Mock).mockResolvedValue([]);
    const newTask = { id: '1', title: 'New Task', status: 'pending' };
    (taskService.createTask as jest.Mock).mockResolvedValue(newTask);
    
    const { result } = renderHook(() => useTasks());
    
    await waitFor(() => expect(result.current.loading).toBe(false));
    
    await act(async () => {
      await result.current.createTask({ title: 'New Task', description: '' });
    });
    
    expect(result.current.tasks).toContainEqual(newTask);
  });
});
```

### Integration Tests

**Auth Routes Integration Tests** (`tests/integration/auth.routes.test.ts`):
```typescript
import request from 'supertest';
import app from '../../src/api/app';
import { sequelize } from '../../src/api/config/database.config';
import { User } from '../../src/models/user.model';

describe('Auth Routes', () => {
  beforeAll(async () => {
    await sequelize.sync({ force: true });
  });

  afterAll(async () => {
    await sequelize.close();
  });

  afterEach(async () => {
    await User.destroy({ where: {} });
  });

  describe('POST /api/auth/register', () => {
    it('should register new user successfully', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({ email: 'test@example.com', password: 'SecurePass123' })
        .expect(201);
      
      expect(response.body.message).toBe('User registered successfully');
      expect(response.body.userId).toBeDefined();
    });

    it('should return 400 for invalid email', async () => {
      const response = await request(app)
        .post('/api/auth/register')
        .send({ email: 'invalid-email', password: 'SecurePass123' })
        .expect(400);
      
      expect(response.body.error.message).toContain('email');
    });

    it('should return 409 for duplicate email', async () => {
      await request(app)
        .post('/api/auth/register')
        .send({ email: 'test@example.com', password: 'SecurePass123' });
      
      const response = await request(app)
        .post('/api/auth/register')
        .send({ email: 'test@example.com', password: 'SecurePass123' })
        .expect(409);
      
      expect(response.body.error.message).toContain('already registered');
    });
  });

  describe('POST /api/auth/login', () => {
    beforeEach(async () => {
      await request(app)
        .post('/api/auth/register')
        .send({ email: 'test@example.com', password: 'SecurePass123' });
    });

    it('should login with valid credentials', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({ email: 'test@example.com', password: 'SecurePass123' })
        .expect(200);
      
      expect(response.body.token).toBeDefined();
      expect(response.body.user.email).toBe('test@example.com');
    });

    it('should return 401 for wrong password', async () => {
      const response = await request(app)
        .post('/api/auth/login')
        .send({ email: 'test@example.com', password: 'WrongPass123' })
        .expect(401);
      
      expect(response.body.error.message).toContain('Invalid credentials');
    });

    it('should return 401 for non-existent email', async () => {
      await request(app)
        .post('/api/auth/login')
        .send({ email: 'wrong@example.com', password: 'SecurePass123' })
        .expect(401);
    });
  });
});
```

**Task Routes Integration Tests** (`tests/integration/tasks.routes.test.ts`):
```typescript
import request from 'supertest';
import app from '../../src/api/app';
import { sequelize } from '../../src/api/config/database.config';
import { User } from '../../src/models/user.model';
import { Task } from '../../src/models/task.model';

describe('Task Routes', () => {
  let authToken: string;
  let userId: string;

  beforeAll(async () => {
    await sequelize.sync({ force: true });
    
    // Register and login user
    const registerRes = await request(app)
      .post('/api/auth/register')
      .send({ email: 'test@example.com', password: 'SecurePass123' });
    
    userId = registerRes.body.userId;
    
    const loginRes = await request(app)
      .post('/api/auth/login')
      .send({ email: 'test@example.com', password: 'SecurePass123' });
    
    authToken = loginRes.body.token;
  });

  afterAll(async () => {
    await sequelize.close();
  });

  afterEach(async () => {
    await Task.destroy({ where: {} });
  });

  describe('GET /api/tasks', () => {
    it('should return empty array when no tasks', async () => {
      const response = await request(app)
        .get('/api/tasks')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);
      
      expect(response.body.tasks).toEqual([]);
    });

    it('should return 401 without auth token', async () => {
      await request(app)
        .get('/api/tasks')
        .expect(401);
    });

    it('should return user tasks only', async () => {
      // Create task for authenticated user
      await Task.create({ userId, title: 'My Task', status: 'pending' });
      
      // Create task for different user
      const otherUser = await User.create({ email: 'other@example.com', passwordHash: 'hash' });
      await Task.create({ userId: otherUser.id, title: 'Other Task', status: 'pending' });
      
      const response = await request(app)
        .get('/api/tasks')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);
      
      expect(response.body.tasks).toHaveLength(1);
      expect(response.body.tasks[0].title).toBe('My Task');
    });

    it('should filter tasks by status', async () => {
      await Task.create({ userId, title: 'Pending Task', status: 'pending' });
      await Task.create({ userId, title: 'Completed Task', status: 'completed' });
      
      const response = await request(app)
        .get('/api/tasks?status=pending')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);
      
      expect(response.body.tasks).toHaveLength(1);
      expect(response.body.tasks[0].status).toBe('pending');
    });
  });

  describe('POST /api/tasks', () => {
    it('should create task with valid data', async () => {
      const response = await request(app)
        .post('/api/tasks')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ title: 'New Task', description: 'Description', status: 'pending' })
        .expect(201);
      
      expect(response.body.title).toBe('New Task');
      expect(response.body.id).toBeDefined();
    });

    it('should return 400 for missing title', async () => {
      await request(app)
        .post('/api/tasks')
        .set('Authorization', `Bearer ${authToken}`)
        .send({ description: 'Description' })
        .expect(400);
    });
  });

  describe('PUT /api/tasks/:id', () => {
    it('should update own task', async () => {
      const task = await Task.create({ userId, title: 'Old Title', status: 'pending' });
      
      const response = await request(app)
        .put(`/api/tasks/${task.id}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({ title: 'New Title' })
        .expect(200);
      
      expect(response.body.title).toBe('New Title');
    });

    it('should return 403 for other user task', async () => {
      const otherUser = await User.create({ email: 'other@example.com', passwordHash: 'hash' });
      const task = await Task.create({ userId: otherUser.id, title: 'Task', status: 'pending' });
      
      await request(app)
        .put(`/api/tasks/${task.id}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({ title: 'New Title' })
        .expect(403);
    });
  });

  describe('DELETE /api/tasks/:id', () => {
    it('should delete own task', async () => {
      const task = await Task.create({ userId, title: 'Task', status: 'pending' });
      
      await request(app)
        .delete(`/api/tasks/${task.id}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);
      
      const deletedTask = await Task.findByPk(task.id);
      expect(deletedTask).toBeNull();
    });

    it('should return 404 for non-existent task', async () => {
      await request(app)
        .delete('/api/tasks/non-existent-id')
        .set('Authorization', `Bearer ${authToken}`)
        .expect(404);
    });
  });
});
```

### E2E Tests

**User Flow E2E Tests** (`tests/e2e/user-flow.test.ts`):
```typescript
import { chromium, Browser, Page } from 'playwright';

describe('Task Tracker E2E', () => {
  let browser: Browser;
  let page: Page;

  beforeAll(async () => {
    browser = await chromium.launch();
  });

  afterAll(async () => {
    await browser.close();
  });

  beforeEach(async () => {
    page = await browser.newPage();
  });

  afterEach(async () => {
    await page.close();
  });

  it('should complete full user journey', async () => {
    // Navigate to app
    await page.goto('http://localhost:5173');

    // Register new user
    await page.click('text=Register');
    await page.fill('input[name="email"]', 'e2e@example.com');
    await page.fill('input[name="password"]', 'SecurePass123');
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await page.waitForURL('**/dashboard');
    expect(await page.textContent('h1')).toContain('My Tasks');

    // Create new task
    await page.click('text=New Task');
    await page.fill('input[name="title"]', 'E2E Test Task');
    await page.fill('textarea[name="description"]', 'Test description');
    await page.click('button:has-text("Create")');

    // Task should appear in list
    await page.waitForSelector('text=E2E Test Task');
    const taskText = await page.textContent('.task-list');
    expect(taskText).toContain('E2E Test Task');

    // Mark task as completed
    await page.click('[data-testid="task-status-toggle"]');
    await page.waitForSelector('.task-item.completed');

    // Edit task
    await page.click('[data-testid="edit-task-button"]');
    await page.fill('input[name="title"]', 'Updated Task Title');
    await page.click('button:has-text("Save")');
    await page.waitForSelector('text=Updated Task Title');

    // Delete task
    await page.click('[data-testid="delete-task-button"]');
    await page.click('button:has-text("Confirm")');
    await page.waitForSelector('text=Updated Task Title', { state: 'detached' });

    // Logout
    await page.click('button:has-text("Logout")');
    await page.waitForURL('**/login');
  });

  it('should persist tasks across sessions', async () => {
    // Login as existing user
    await page.goto('http://localhost:5173/login');
    await page.fill('input[name="email"]', 'e2e@example.com');
    await page.fill('input[name="password"]', 'SecurePass123');
    await page.click('button[type="submit"]');

    // Create task
    await page.click('text=New Task');
    await page.fill('input[name="title"]', 'Persistent Task');
    await page.click('button:has-text("Create")');
    await page.waitForSelector('text=Persistent Task');

    // Logout
    await page.click('button:has-text("Logout")');

    // Login again
    await page.fill('input[name="email"]', 'e2e@example.com');
    await page.fill('input[name="password"]', 'SecurePass123');
    await page.click('button[type="submit"]');

    // Task should still be there
    await page.waitForSelector('text=Persistent Task');
  });

  it('should handle validation errors gracefully', async () => {
    await page.goto('http://localhost:5173/login');

    // Try to submit empty form
    await page.click('button[type="submit"]');
    expect(await page.textContent('.error')).toContain('required');

    // Try invalid email
    await page.fill('input[name="email"]', 'invalid-email');
    await page.fill('input[name="password"]', 'password');
    await page.click('button[type="submit"]');
    expect(await page.textContent('.error')).toContain('email');
  });

  it('should show error for wrong credentials', async () => {
    await page.goto('http://localhost:5173/login');
    await page.fill('input[name="email"]', 'wrong@example.com');
    await page.fill('input[name="password"]', 'WrongPass123');
    await page.click('button[type="submit"]');

    await page.waitForSelector('text=Invalid credentials');
  });
});
```

---

## 10. Migration Strategy

<!-- AI: How to migrate from current state to new implementation -->

### Phase 1: Infrastructure Setup (Week 1)

**1.1 Database Setup**:
```bash
# Create PostgreSQL database
createdb tasktracker_dev
createdb tasktracker_test

# Configure environment variables
cp .env.example .env.development
# Edit .env.development with database credentials
```

**1.2 Backend Project Initialization**:
```bash
# Initialize Node.js project
npm init -y

# Install backend dependencies
npm install express typescript ts-node @types/node @types/express
npm install sequelize pg pg-hstore
npm install bcrypt jsonwebtoken
npm install cors helmet compression morgan
npm install joi express-validator
npm install dotenv winston

# Install dev dependencies
npm install --save-dev nodemon @types/bcrypt @types/jsonwebtoken
npm install --save-dev jest @types/jest ts-jest supertest @types/supertest
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
npm install --save-dev prettier

# Setup TypeScript configuration
npx tsc --init
```

**1.3 Frontend Project Initialization**:
```bash
# Create frontend project with Vite
npm create vite@latest frontend -- --template react-ts

# Install frontend dependencies
cd frontend
npm install react-router-dom axios
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**1.4 Docker Setup**:
```bash
# Create Dockerfiles and docker-compose.yml
# Start PostgreSQL container for development
docker-compose up -d postgres
```

### Phase 2: Backend Core Implementation (Week 2-3)

**2.1 Database Models and Migrations**:
```bash
# Run migrations in order
npx ts-node src/models/migrations/001-create-users-table.ts
npx ts-node src/models/migrations/002-create-tasks-table.ts
npx ts-node src/models/migrations/003-add-indexes.ts

# Verify schema
psql tasktracker_dev -c "\dt"
psql tasktracker_dev -c "\d users"
psql tasktracker_dev -c "\d tasks"
```

**2.2 Authentication Implementation**:
- Implement User model (`src/models/user.model.ts`)
- Implement JWT utilities (`src/api/utils/jwt.util.ts`)
- Implement password utilities (`src/api/utils/password.util.ts`)
- Implement UserRepository (`src/api/repositories/user.repository.ts`)
- Implement AuthService (`src/api/services/auth.service.ts`)
- Implement AuthController (`src/api/controllers/auth.controller.ts`)
- Implement auth routes (`src/api/routes/auth.routes.ts`)
- Implement auth middleware (`src/api/middleware/auth.middleware.ts`)
- Write unit tests for each component

**2.3 Task Management Implementation**:
- Implement Task model (`src/models/task.model.ts`)
- Implement TaskRepository (`src/api/repositories/task.repository.ts`)
- Implement TasksService (`src/api/services/tasks.service.ts`)
- Implement TasksController (`src/api/controllers/tasks.controller.ts`)
- Implement task routes (`src/api/routes/tasks.routes.ts`)
- Write unit tests for each component

**2.4 Server Setup**:
- Implement Express app configuration (`src/api/app.ts`)
- Implement server initialization (`src/api/server.ts`)
- Implement error handling middleware (`src/api/middleware/error.middleware.ts`)
- Implement validation middleware (`src/api/middleware/validation.middleware.ts`)
- Test server manually with Postman/curl

### Phase 3: Frontend Implementation (Week 3-4)

**3.1 Authentication UI**:
- Setup routing with React Router (`frontend/src/App.tsx`)
- Implement AuthContext (`frontend/src/context/AuthContext.tsx`)
- Implement auth service (`frontend/src/services/auth.service.ts`)
- Implement API service with interceptors (`frontend/src/services/api.service.ts`)
- Implement LoginPage (`frontend/src/pages/LoginPage.tsx`)
- Implement RegisterPage (`frontend/src/pages/RegisterPage.tsx`)
- Implement PrivateRoute (`frontend/src/components/PrivateRoute.tsx`)

**3.2 Task Management UI**:
- Implement task service (`frontend/src/services/task.service.ts`)
- Implement useTasks hook (`frontend/src/hooks/useTasks.ts`)
- Implement TasksDashboard (`frontend/src/pages/TasksDashboard.tsx`)
- Implement TaskList (`frontend/src/components/TaskList.tsx`)
- Implement TaskItem (`frontend/src/components/TaskItem.tsx`)
- Implement TaskForm (`frontend/src/components/TaskForm.tsx`)
- Implement TaskFilter (`frontend/src/components/TaskFilter.tsx`)
- Implement Header with logout (`frontend/src/components/Header.tsx`)

**3.3 Styling**:
- Configure Tailwind CSS
- Create global styles (`frontend/src/styles/index.css`)
- Add responsive design for mobile devices
- Add loading states and error messages

### Phase 4: Integration Testing (Week 4)

**4.1 Backend Integration Tests**:
```bash
# Setup test database
createdb tasktracker_test

# Run integration tests
npm run test:integration

# Verify all endpoints work correctly
```

**4.2 End-to-End Testing**:
```bash
# Install Playwright
npm install --save-dev @playwright/test

# Run E2E tests
npm run test:e2e
```

**4.3 Manual Testing**:
- Complete user registration flow
- Login with valid and invalid credentials
- Create, read, update, delete tasks
- Test task status filtering
- Test authorization (access control)
- Test error handling

### Phase 5: Deployment Preparation (Week 5)

**5.1 Docker Containerization**:
```bash
# Build backend container
docker build -f Dockerfile.backend -t tasktracker-backend .

# Build frontend container
docker build -f Dockerfile.frontend -t tasktracker-frontend .

# Test full stack with docker-compose
docker-compose up
```

**5.2 Production Configuration**:
- Setup production environment variables
- Configure HTTPS/SSL certificates
- Setup Nginx reverse proxy
- Configure CORS for production domain
- Setup database connection pooling
- Configure logging for production

**5.3 CI/CD Pipeline**:
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
      - run: npm install
      - run: npm run test
      - run: npm run test:integration

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: docker build -f Dockerfile.backend -t backend .
      - run: docker build -f Dockerfile.frontend -t frontend .

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          # Deploy commands here
```

### Phase 6: Deployment and Launch (Week 5-6)

**6.1 Staging Deployment**:
- Deploy to staging environment
- Run smoke tests
- Perform load testing
- Fix any issues found

**6.2 Production Deployment**:
- Deploy to production
- Run health checks
- Monitor logs and metrics
- Setup alerting

**6.3 Post-Launch**:
- Monitor application performance
- Track user registrations
- Monitor error rates
- Collect user feedback

### Data Migration Notes

**No Legacy Data**:
- This is a new application with no existing data
- Start with clean database schema
- Seed test data for development/staging:

```typescript
// scripts/seed-data.ts
import { User } from './src/models/user.model';
import { Task } from './src/models/task.model';
import { hashPassword } from './src/api/utils/password.util';

async function seedData() {
  // Create test users
  const user1 = await User.create({
    email: 'demo@example.com',
    passwordHash: await hashPassword('DemoPass123')
  });

  // Create sample tasks
  await Task.bulkCreate([
    { userId: user1.id, title: 'Complete project documentation', status: 'pending' },
    { userId: user1.id, title: 'Review pull requests', status: 'pending' },
    { userId: user1.id, title: 'Setup CI/CD pipeline', status: 'completed' }
  ]);

  console.log('Seed data created successfully');
}
```

---

## 11. Rollback Plan

<!-- AI: How to rollback if deployment fails -->

### Rollback Triggers

**When to Rollback**:
- Critical bugs affecting core functionality (auth, task CRUD)
- Database corruption or data loss
- Performance degradation (>5s response times)
- Security vulnerabilities discovered post-deployment
- Error rate >10% for more than 5 minutes
- Complete service outage

**When NOT to Rollback**:
- Minor UI bugs that don't block functionality
- Non-critical features failing
- Single user reports (investigate first)
- Performance issues affecting <5% of users

### Rollback Procedures

### 1. Application Rollback (Docker/Kubernetes)

**Docker Compose Rollback**:
```bash
# List recent images
docker images tasktracker-backend --format "{{.Tag}} {{.CreatedAt}}"

# Stop current containers
docker-compose down

# Edit docker-compose.yml to use previous image tag
# Change: image: tasktracker-backend:v1.2.0
# To:     image: tasktracker-backend:v1.1.0

# Start with previous version
docker-compose up -d

# Verify health
curl http://localhost:3000/api/health
```

**Kubernetes Rollback**:
```bash
# Check deployment history
kubectl rollout history deployment/tasktracker-backend

# Rollback to previous version
kubectl rollout undo deployment/tasktracker-backend

# Rollback to specific revision
kubectl rollout undo deployment/tasktracker-backend --to-revision=3

# Monitor rollback progress
kubectl rollout status deployment/tasktracker-backend

# Verify pods are running
kubectl get pods -l app=tasktracker-backend
```

**AWS ECS Rollback**:
```bash
# List task definitions
aws ecs list-task-definitions --family-prefix tasktracker-backend

# Update service to use previous task definition
aws ecs update-service \
  --cluster tasktracker-cluster \
  --service tasktracker-backend-service \
  --task-definition tasktracker-backend:5

# Monitor service stability
aws ecs describe-services \
  --cluster tasktracker-cluster \
  --services tasktracker-backend-service
```

### 2. Database Rollback

**Migration Rollback**:
```bash
# Check current migration version
npx sequelize-cli db:migrate:status

# Rollback last migration
npx sequelize-cli db:migrate:undo

# Rollback to specific migration
npx sequelize-cli db:migrate:undo:all --to 002-create-tasks-table.ts

# Verify schema
psql tasktracker_prod -c "\d tasks"
```

**Database Restore from Backup**:
```bash
# List available backups (AWS RDS example)
aws rds describe-db-snapshots \
  --db-instance-identifier tasktracker-db

# Restore from snapshot (creates new instance)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier tasktracker-db-restored \
  --db-snapshot-identifier tasktracker-db-snapshot-2026-02-01

# Point application to restored database
# Update DATABASE_URL environment variable
# Restart application
```

**Point-in-Time Recovery** (AWS RDS):
```bash
# Restore to specific timestamp
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier tasktracker-db \
  --target-db-instance-identifier tasktracker-db-pitr \
  --restore-time 2026-02-02T10:00:00Z

# Update connection string and restart
```

### 3. Frontend Rollback

**CDN/Static Asset Rollback**:
```bash
# If using versioned deployments, update symlink or CDN to point to previous version

# S3 + CloudFront example
aws s3 sync s3://tasktracker-frontend-backups/v1.1.0/ s3://tasktracker-frontend/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id E1234567890ABC \
  --paths "/*"

# Verify rollback
curl https://app.example.com/assets/main.js | grep "version"
```

### 4. Configuration Rollback

**Environment Variables**:
```bash
# Kubernetes ConfigMap rollback
kubectl get configmap tasktracker-config -o yaml > config-backup.yaml

# Apply previous configuration
kubectl apply -f config-previous.yaml

# Restart pods to pick up new config
kubectl rollout restart deployment/tasktracker-backend
```

**Secrets Rollback**:
```bash
# Retrieve previous secret version (AWS Secrets Manager)
aws secretsmanager get-secret-value \
  --secret-id tasktracker/jwt-secret \
  --version-stage AWSPREVIOUS

# Update to previous version
aws secretsmanager update-secret-version-stage \
  --secret-id tasktracker/jwt-secret \
  --version-stage AWSCURRENT \
  --move-to-version-id <previous-version-id>
```

### 5. Rollback Verification Checklist

After rollback, verify:

```bash
# 1. Health checks pass
curl http://localhost:3000/api/health
# Expected: {"status": "healthy", ...}

# 2. Authentication works
curl -X POST http://localhost:3000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
# Expected: 200 OK with token

# 3. Task endpoints work
curl http://localhost:3000/api/tasks \
  -H "Authorization: Bearer $TOKEN"
# Expected: 200 OK with tasks array

# 4. Database connectivity
psql tasktracker_prod -c "SELECT COUNT(*) FROM users;"
# Expected: Row count returned

# 5. Error rate normalized
# Check monitoring dashboard for error rate <1%

# 6. Response times acceptable
# Check p95 response time <500ms

# 7. Frontend loads correctly
curl https://app.example.com
# Expected: 200 OK with HTML
```

### 6. Rollback Communication Plan

**Internal Communication**:
```
1. Notify team in Slack/Discord:
   "🚨 ROLLBACK IN PROGRESS: Rolling back to v1.1.0 due to [reason]. ETA: 10 minutes."

2. Update status page:
   "We are experiencing issues and rolling back to a previous version. Service should be restored shortly."

3. Post-rollback message:
   "✅ Rollback complete. Service restored to v1.1.0. Investigating root cause."
```

**User Communication** (if downtime occurred):
```
Subject: Service Disruption - Resolved

We experienced a brief service disruption today at [time] due to a deployment issue. 
Our team immediately rolled back the changes and service has been fully restored.

No user data was lost. All tasks and accounts are intact.

We apologize for the inconvenience and have implemented additional safeguards to prevent similar issues.
```

### 7. Post-Rollback Actions

**Immediate Actions**:
1. Verify all systems operational
2. Monitor error rates and performance for 1 hour
3. Review logs to identify root cause
4. Document what went wrong
5. Cancel any scheduled deployments

**Follow-Up Actions**:
1. Conduct post-mortem meeting within 24 hours
2. Identify root cause and contributing factors
3. Create action items to prevent recurrence
4. Update deployment checklist
5. Improve monitoring/alerting if needed
6. Fix the issue in development
7. Add tests to catch the issue
8. Re-deploy with proper testing

**Post-Mortem Template**:
```markdown
# Incident Post-Mortem: [Date] Deployment Rollback

## Summary
[Brief description of what happened]

## Timeline
- [Time]: Deployment started
- [Time]: Issue detected
- [Time]: Rollback initiated
- [Time]: Service restored

## Root Cause
[What caused the issue]

## Impact
- Duration: [X minutes]
- Users affected: [number or percentage]
- Data loss: None / [description]

## Action Items
1. [ ] [Preventive measure 1]
2. [ ] [Preventive measure 2]
3. [ ] [Process improvement]

## Lessons Learned
[What we learned and how we'll improve]
```

### 8. Rollback Testing

**Regular Rollback Drills** (Quarterly):
```bash
# Schedule rollback drill in staging environment
# 1. Deploy current version
# 2. Deploy intentionally broken version
# 3. Detect issues via monitoring
# 4. Execute rollback procedure
# 5. Verify service restoration
# 6. Time the process and document
```

---

## 12. Performance Considerations

<!-- AI: Performance optimizations, caching, indexing -->

### Database Performance

**Indexing Strategy**:

```sql
-- Primary indexes (already in migrations)
CREATE INDEX tasks_user_id_idx ON tasks(user_id);
CREATE INDEX tasks_user_id_status_idx ON tasks(user_id, status);
CREATE INDEX tasks_created_at_idx ON tasks(created_at);
CREATE UNIQUE INDEX users_email_unique_idx ON users(email);

-- Query analysis
EXPLAIN ANALYZE SELECT * FROM tasks WHERE user_id = 'uuid' AND status = 'pending';
-- Expected: Index Scan using tasks_user_id_status_idx

-- Monitor slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
WHERE mean_exec_time > 100 
ORDER BY mean_exec_time DESC;
```

**Connection Pooling Configuration**:

```typescript
// src/api/config/database.config.ts
export const sequelize = new Sequelize(process.env.DATABASE_URL!, {
  dialect: 'postgres',
  pool: {
    max: 20,          // Maximum connections
    min: 5,           // Minimum connections
    acquire: 30000,   // Maximum time to acquire connection (ms)
    idle: 10000       // Maximum idle time before release (ms)
  },
  logging: process.env.NODE_ENV === 'development' ? console.log : false
});
```

**Query Optimization**:

```typescript
// Efficient: Use indexed columns in WHERE clause
taskRepository.findAll({
  where: { userId: 'uuid', status: 'pending' },  // Uses composite index
  order: [['createdAt', 'DESC']],                 // Uses index
  limit: 50                                        // Pagination
});

// Inefficient: Full table scan
taskRepository.findAll({
  where: {
    description: { [Op.like]: '%keyword%' }  // No index on description
  }
});

// Optimized with pagination
async function getPaginatedTasks(userId: string, page: number = 1, limit: number = 50) {
  const offset = (page - 1) * limit;
  return Task.findAndCountAll({
    where: { userId },
    limit,
    offset,
    order: [['createdAt', 'DESC']]
  });
}
```

**Database Monitoring**:

```sql
-- Check table sizes
SELECT 
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check index usage
SELECT 
  schemaname,
  tablename,
  indexname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;  -- Low idx_scan = unused index

-- Vacuum and analyze regularly
VACUUM ANALYZE tasks;
VACUUM ANALYZE users;
```

### API Performance

**Response Compression**:

```typescript
// Already in app.ts
import compression from 'compression';
app.use(compression({
  threshold: 1024,  // Only compress responses > 1KB
  level: 6          // Compression level (0-9, higher = more compression)
}));
```

**Request Validation Caching**:

```typescript
// Cache compiled Joi schemas
const schemaCache = new Map<string, Schema>();

export const validateRequest = (schemaKey: string, schema: Schema) => {
  if (!schemaCache.has(schemaKey)) {
    schemaCache.set(schemaKey, schema);
  }
  
  return (req: Request, res: Response, next: NextFunction) => {
    const cachedSchema = schemaCache.get(schemaKey)!;
    const { error } = cachedSchema.validate(req.body);
    // ... validation logic
  };
};
```

**Pagination for Large Result Sets**:

```typescript
// src/api/controllers/tasks.controller.ts
getTasks = async (req: AuthRequest, res: Response, next: NextFunction) => {
  try {
    const userId = req.user!.id;
    const status = req.query.status as TaskStatus | undefined;
    const page = parseInt(req.query.page as string) || 1;
    const limit = Math.min(parseInt(req.query.limit as string) || 50, 100);
    
    const { tasks, total } = await this.tasksService.getUserTasksPaginated(
      userId, 
      status, 
      page, 
      limit
    );
    
    res.status(200).json({
      tasks,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    next(error);
  }
};
```

**Response Time Monitoring**:

```typescript
// src/api/middleware/performance.middleware.ts
export const performanceMonitoring = (req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    
    logger.info({
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration: `${duration}ms`,
      userId: (req as any).user?.id
    });
    
    // Alert on slow requests
    if (duration > 1000) {
      logger.warn(`Slow request detected: ${req.method} ${req.path} took ${duration}ms`);
    }
  });
  
  next();
};

// Apply in app.ts
app.use(performanceMonitoring);
```

### Frontend Performance

**Code Splitting and Lazy Loading**:

```typescript
// frontend/src/App.tsx
import { lazy, Suspense } from 'react';

const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const TasksDashboard = lazy(() => import('./pages/TasksDashboard'));

function App() {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/dashboard" element={<TasksDashboard />} />
      </Routes>
    </Suspense>
  );
}
```

**Memoization to Prevent Re-renders**:

```typescript
// frontend/src/components/TaskItem.tsx
import { memo } from 'react';

export const TaskItem = memo<TaskItemProps>(({ task, onEdit, onDelete, onStatusChange }) => {
  // Component logic
}, (prevProps, nextProps) => {
  // Custom comparison: only re-render if task changed
  return prevProps.task.id === nextProps.task.id &&
         prevProps.task.title === nextProps.task.title &&
         prevProps.task.status === nextProps.task.status;
});
```

**Debounced Search/Filter**:

```typescript
// frontend/src/hooks/useDebounce.ts
import { useEffect, useState } from 'react';

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => clearTimeout(handler);
  }, [value, delay]);

  return debouncedValue;
}

// Usage in search component
const [searchTerm, setSearchTerm] = useState('');
const debouncedSearch = useDebounce(searchTerm, 300);

useEffect(() => {
  if (debouncedSearch) {
    // Perform search
  }
}, [debouncedSearch]);
```

**Bundle Size Optimization**:

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['tailwindcss'],
        }
      }
    },
    chunkSizeWarningLimit: 1000,
    sourcemap: false  // Disable sourcemaps in production
  }
});
```

**Image and Asset Optimization**:

```typescript
// Lazy load images
<img 
  src={imageUrl} 
  loading="lazy" 
  alt={description}
/>

// Use WebP format with fallback
<picture>
  <source srcSet="image.webp" type="image/webp" />
  <img src="image.png" alt="description" />
</picture>
```

### Caching Strategy (Future Enhancement)

**Redis Caching Layer** (when needed):

```typescript
// src/api/services/cache.service.ts
import Redis from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

export class CacheService {
  /**
   * Get user tasks from cache or database
   */
  async getUserTasks(userId: string): Promise<Task[]> {
    const cacheKey = `user:${userId}:tasks`;
    
    // Try cache first
    const cached = await redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }
    
    // Fetch from database
    const tasks = await taskRepository.findByUserId(userId);
    
    // Cache for 5 minutes
    await redis.setex(cacheKey, 300, JSON.stringify(tasks));
    
    return tasks;
  }
  
  /**
   * Invalidate cache on task mutation
   */
  async invalidateUserTasksCache(userId: string): Promise<void> {
    const cacheKey = `user:${userId}:tasks`;
    await redis.del(cacheKey);
  }
}
```

**HTTP Caching Headers**:

```typescript
// For static assets (served by Nginx)
location /assets/ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}

// For API responses (dynamic data)
app.get('/api/tasks', authenticate, (req, res) => {
  res.set('Cache-Control', 'private, no-cache, no-store, must-revalidate');
  // ... response logic
});
```

### Load Testing

**Artillery Load Test Configuration**:

```yaml
# load-test.yml
config:
  target: 'http://localhost:3000'
  phases:
    - duration: 60
      arrivalRate: 10
      name: Warm up
    - duration: 120
      arrivalRate: 50
      name: Sustained load
    - duration: 60
      arrivalRate: 100
      name: Peak load

scenarios:
  - name: "User Journey"
    flow:
      - post:
          url: "/api/auth/login"
          json:
            email: "test@example.com"
            password: "SecurePass123"
          capture:
            - json: "$.token"
              as: "authToken"
      - get:
          url: "/api/tasks"
          headers:
            Authorization: "Bearer {{ authToken }}"
      - post:
          url: "/api/tasks"
          headers:
            Authorization: "Bearer {{ authToken }}"
          json:
            title: "Load test task"
            status: "pending"
```

```bash
# Run load test
npm install -g artillery
artillery run load-test.yml

# Generate report
artillery run --output report.json load-test.yml
artillery report report.json
```

**Performance Benchmarks**:

| Metric | Target | Measured |
|--------|--------|----------|
| API response time (p50) | <200ms | TBD |
| API response time (p95) | <500ms | TBD |
| API response time (p99) | <1000ms | TBD |
| Page load time (First Contentful Paint) | <1.5s | TBD |
| Page load time (Time to Interactive) | <3s | TBD |
| Bundle size (initial) | <200KB (gzip) | TBD |
| Database query time (indexed) | <50ms | TBD |
| Concurrent users supported | 100 | TBD |
| Requests per second (single instance) | 100 | TBD |

---

## Appendix: Existing Repository Structure

## Repository File Structure

```
.claude-output.json
.claude-plan.json
.claude-resolution.json
.conflict-info.json
.git
.gitignore
.pr-number
CONTRIBUTING.md
LICENSE
README.md
docs/
  getting_started.md
  plans/
    health-check/
      HLD.md
      LLD.md
      PRD.md
    task-tracker/
      HLD.md
      PRD.md
notebooks/
  README.md
random_colors.py
random_words.py
requirements.txt
src/
  analysis/
    README.md
  api/
    README.md
    __init__.py
    main.py
  models/
    README.md
  random_words.py
  visualization/
    README.md
test_api.py
test_random_colors.py
test_random_words.py
```
