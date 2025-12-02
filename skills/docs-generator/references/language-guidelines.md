# Language Guidelines

Guidelines for writing documentation in different languages.

## General Principles

1. **Consistency**: Use the same terms throughout
2. **Clarity**: Prefer simple constructions over complex ones
3. **Technical terms**: Keep English technical terms when no established translation exists
4. **Code**: Code, commands, and file names stay in English
5. **Examples**: Adapt examples to be culturally appropriate

## Language-Specific Guidelines

### English (en)

**Style**: Clear, direct, professional

| Aspect | Guideline |
|--------|-----------|
| Voice | Active ("Create a file") not passive ("A file is created") |
| Person | Second person ("You can..." / "Run...") |
| Contractions | OK in guides, avoid in reference |
| Technical terms | Use standard industry terminology |

**Example**:
> Run the following command to start the server:
> ```bash
> npm start
> ```

### Dutch (nl)

**Style**: Direct but polite, professional

| Aspect | Guideline |
|--------|-----------|
| Voice | Active ("Maak een bestand aan") |
| Person | Second person formal ("U kunt...") or informal ("Je kunt...") - be consistent |
| Technical terms | Keep English terms for: API, endpoint, server, database, token |
| Translate | bestand (file), map (folder), opdracht (command), uitvoeren (run) |

**Common translations**:
| English | Dutch |
|---------|-------|
| File | Bestand |
| Folder/Directory | Map |
| Run/Execute | Uitvoeren |
| Configuration | Configuratie |
| Settings | Instellingen |
| Install | Installeren |
| Create | Aanmaken |
| Delete | Verwijderen |
| Update | Bijwerken |

**Example**:
> Voer de volgende opdracht uit om de server te starten:
> ```bash
> npm start
> ```

### German (de)

**Style**: Formal, precise, thorough

| Aspect | Guideline |
|--------|-----------|
| Voice | Active preferred |
| Person | "Sie" (formal) for professional docs |
| Technical terms | Keep English for: API, Server, Token, Framework |
| Compound words | Use German compounds when natural |

**Common translations**:
| English | German |
|---------|--------|
| File | Datei |
| Folder | Ordner |
| Run/Execute | Ausführen |
| Configuration | Konfiguration |
| Settings | Einstellungen |
| Install | Installieren |
| Create | Erstellen |
| Delete | Löschen |
| Update | Aktualisieren |

**Example**:
> Führen Sie den folgenden Befehl aus, um den Server zu starten:
> ```bash
> npm start
> ```

### French (fr)

**Style**: Formal, elegant, clear

| Aspect | Guideline |
|--------|-----------|
| Voice | Active preferred |
| Person | "Vous" (formal) |
| Technical terms | Keep English for most tech terms |
| Articles | Pay attention to gender of technical terms |

**Common translations**:
| English | French |
|---------|--------|
| File | Fichier (m) |
| Folder | Dossier (m) |
| Run/Execute | Exécuter |
| Configuration | Configuration (f) |
| Settings | Paramètres (m) |
| Install | Installer |
| Create | Créer |
| Delete | Supprimer |
| Update | Mettre à jour |

**Example**:
> Exécutez la commande suivante pour démarrer le serveur :
> ```bash
> npm start
> ```

### Spanish (es)

**Style**: Clear, professional, friendly

| Aspect | Guideline |
|--------|-----------|
| Voice | Active preferred |
| Person | "Usted" (formal) or "tú" (informal) - be consistent |
| Technical terms | Keep English for most tech terms |
| Regional | Use neutral Spanish (avoid regional idioms) |

**Common translations**:
| English | Spanish |
|---------|---------|
| File | Archivo |
| Folder | Carpeta |
| Run/Execute | Ejecutar |
| Configuration | Configuración |
| Settings | Ajustes/Configuración |
| Install | Instalar |
| Create | Crear |
| Delete | Eliminar |
| Update | Actualizar |

**Example**:
> Ejecute el siguiente comando para iniciar el servidor:
> ```bash
> npm start
> ```

## What to Keep in English

Always keep in English:
- Code snippets and variable names
- File names and paths
- Command-line commands
- API names and endpoints
- Error messages (quote original)
- Brand names and product names
- Standard acronyms (API, HTTP, JSON, SQL)

## Structural Elements

Keep structure consistent across languages:

| Element | Guideline |
|---------|-----------|
| Headings | Translate |
| Code blocks | Keep English |
| Tables | Translate headers and descriptions |
| Lists | Translate content |
| Links | Keep URLs, translate link text |
| Notes/Warnings | Translate, keep format |

## Formatting

| Language | Quote marks | List separator |
|----------|-------------|----------------|
| English | "quotes" | item, item, and item |
| Dutch | "aanhalingstekens" | item, item en item |
| German | „Anführungszeichen" | item, item und item |
| French | « guillemets » | item, item et item |
| Spanish | «comillas» | item, item e item |

## Asking User for Clarification

When uncertain about language choice:
- "Should I use formal (Sie/Vous/Usted) or informal (du/tu/tú) address?"
- "Should technical terms like 'endpoint' be translated or kept in English?"
- "Is this for a specific region (e.g., Latin American Spanish vs European Spanish)?"
