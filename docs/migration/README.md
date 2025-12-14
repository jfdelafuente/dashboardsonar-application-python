# Migration Documentation

Guía para migrar código legacy a la nueva arquitectura en capas.

---

## 📚 Contenido

- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Guía completa de migración
  - Ejemplos Before/After para cada capa
  - Proceso paso a paso de migración
  - Migración de SQL queries a repositorios
  - Migración de lógica de negocio a servicios
  - Refactorización de vistas
  - Checklist completo
  - FAQ con preguntas comunes

---

## 🎯 ¿Cuándo Usar Esta Guía?

Esta guía es útil si:

- ✅ Tienes código legacy con SQL directo en vistas
- ✅ Necesitas migrar lógica de negocio a servicios
- ✅ Quieres refactorizar vistas gordas (>50 LOC)
- ✅ Estás agregando nuevas features y quieres hacerlo bien
- ✅ Necesitas entender la arquitectura objetivo

---

## 🚀 Proceso de Migración (Resumen)

### Paso 1: Identificar Código Legacy

```python
# ❌ LEGACY: Vista con SQL directo
@app.route('/users')
def users():
    users = User.query.filter(User.active == True).all()
    total = len(users)
    return render_template('users.html', users=users, total=total)
```

### Paso 2: Crear Repository

```python
# ✅ NUEVO: Repository con query
class UserRepository(BaseRepository[User]):
    def get_active_users(self) -> List[User]:
        return self.session.query(User)\
            .filter(User.active == True)\
            .all()
```

### Paso 3: Crear Service

```python
# ✅ NUEVO: Service con lógica de negocio
class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    def get_active_users_summary(self) -> Dict[str, Any]:
        users = self.user_repo.get_active_users()
        return {
            'users': [u.to_dict() for u in users],
            'total': len(users)
        }
```

### Paso 4: Refactorizar Vista

```python
# ✅ NUEVO: Vista delgada
@app.route('/users')
@inject_service(UserService)
def users(user_service: UserService):
    data = user_service.get_active_users_summary()
    return render_template('users.html', **data)
```

Ver proceso completo en [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md).

---

## 📊 Checklist de Migración

- [ ] **Paso 1**: Crear Repository con queries SQL
- [ ] **Paso 2**: Crear tests para Repository
- [ ] **Paso 3**: Crear Service con lógica de negocio
- [ ] **Paso 4**: Crear tests para Service (con mocks)
- [ ] **Paso 5**: Refactorizar Vista (delgada, <30 LOC)
- [ ] **Paso 6**: Verificar tests pasan
- [ ] **Paso 7**: Code review y merge

---

## 🔗 Enlaces Relacionados

- [ARCHITECTURE.md](../ARCHITECTURE.md) - Entender arquitectura objetivo
- [DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md) - Cómo crear Repositories y Services
- [CONTRIBUTING.md](../../CONTRIBUTING.md) - Estándares de código

---

**Última actualización**: 2025-12-14
