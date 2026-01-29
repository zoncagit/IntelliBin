# 🚀 Launch Guide: SAFEBIN Flutter Version

To see the high-fidelity preview of the 2nd version, follow these steps:

## 1. Setup Flutter Environment
Since Flutter is a native SDK, you need to have it in your system PATH.
- **Download**: [Flutter SDK Windows](https://storage.googleapis.com/flutter_infra_release/releases/stable/windows/flutter_windows_3.27.1-stable.zip)
- **Extract**: Move it to `C:\src\flutter`
- **PATH**: Add `C:\src\flutter\bin` to your User Environment Variables.

## 2. Initialize Project
Open a terminal in the project directory:
```powershell
cd "c:\Users\WINDOWS\Desktop\iyad\BLAST HACKATHON\safebi_mobile2ndversion"
flutter pub get
```

## 3. Launch Web Preview
Run this command to start the interactive web version:
```powershell
flutter run -d chrome --web-renderer canvaskit
```

> [!TIP]
> Using `--web-renderer canvaskit` ensures the 3D model and complex shaders render with maximum fidelity.

## 4. Troubleshooting
- If you see `Command not found`, restart your terminal/IDE after updating the PATH.
- Run `flutter doctor` to check if anything else is missing.
