import yt_dlp
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import shutil
import urllib.request
import zipfile
import platform

class DownloadApp:
    def __init__(self, window):
        self.window = window
        window.title("Mamon's YouTube Downloader v1.0")
        window.geometry("520x480")
        window.resizable(False, False)

        # Title
        title_label = tk.Label(window, text="Mamon's YouTube Downloader", font=("Arial", 16, "bold"), fg="#2196F3")
        title_label.pack(pady=10)

        # FFmpeg Status Section
        ffmpeg_frame = tk.LabelFrame(window, text="FFmpeg Status", padx=10, pady=5)
        ffmpeg_frame.pack(pady=5, padx=10, fill="x")
        
        self.ffmpeg_status_label = tk.Label(ffmpeg_frame, text="Checking...", fg="orange", font=("Arial", 9))
        self.ffmpeg_status_label.pack(side=tk.LEFT)
        
        self.setup_ffmpeg_btn = tk.Button(ffmpeg_frame, text="Setup FFmpeg", 
                                          command=self.setup_ffmpeg_dialog, bg="#4CAF50", fg="white")
        self.setup_ffmpeg_btn.pack(side=tk.RIGHT, padx=5)

        # URL input
        url_label = tk.Label(window, text="Enter YouTube URL:", font=("Arial", 10))
        url_label.pack(pady=(10,0))
        self.url_entry = tk.Entry(window, width=60, font=("Arial", 10))
        self.url_entry.pack(pady=5)

        # Folder selection
        folder_label = tk.Label(window, text="Save to folder:", font=("Arial", 10))
        folder_label.pack()
        frame = tk.Frame(window)
        frame.pack()
        self.folder_entry = tk.Entry(frame, width=45, font=("Arial", 10))
        self.folder_entry.pack(side=tk.LEFT, padx=5)
        
        # Set default download folder
        default_folder = os.path.join(os.path.expanduser("~"), "Downloads")
        self.folder_entry.insert(0, default_folder)
        
        browse_btn = tk.Button(frame, text="Browse", command=self.browse_folder)
        browse_btn.pack(side=tk.LEFT)

        # Resolution dropdown
        res_label = tk.Label(window, text="Select Resolution:", font=("Arial", 10))
        res_label.pack(pady=5)
        self.res_var = tk.StringVar(value="best")
        self.res_menu = ttk.Combobox(window, textvariable=self.res_var,
                                     values=["360p", "480p", "720p", "1080p", "best"],
                                     state="readonly", width=15, font=("Arial", 10))
        self.res_menu.pack()

        # Progress bar
        progress_label = tk.Label(window, text="Progress:", font=("Arial", 10))
        progress_label.pack(pady=(10,0))
        self.progress = ttk.Progressbar(window, length=420, mode="determinate")
        self.progress.pack(pady=5)

        # Status text
        self.status_label = tk.Label(window, text="Ready to download", font=("Arial", 9), fg="blue")
        self.status_label.pack()

        # Download button
        download_btn = tk.Button(window, text="Download Video", width=20, height=2,
                                command=self.start_download, bg="#2196F3", fg="white",
                                font=("Arial", 11, "bold"), cursor="hand2")
        download_btn.pack(pady=15)

        # Footer
        footer_label = tk.Label(window, text="Created by Mamon | Supports YouTube, Vimeo, and 1000+ sites", 
                font=("Arial", 8), fg="gray")
        footer_label.pack(side=tk.BOTTOM, pady=5)

        # Initialize FFmpeg
        self.ffmpeg_path = None
        self.check_ffmpeg()

    def check_ffmpeg(self):
        """Check if FFmpeg is available"""
        # Determine base directory
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            app_dir = os.path.dirname(sys.executable)
            # Also check _MEIPASS for PyInstaller temp extraction
            if hasattr(sys, '_MEIPASS'):
                meipass_ffmpeg = os.path.join(sys._MEIPASS, "ffmpeg", "bin", "ffmpeg.exe")
                if os.path.exists(meipass_ffmpeg):
                    self.ffmpeg_path = meipass_ffmpeg
                    self.ffmpeg_status_label.config(text="FFmpeg Ready (Bundled)", fg="green")
                    return True
        else:
            # Running as script
            app_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Check various possible locations
        possible_paths = [
            os.path.join(app_dir, "ffmpeg", "bin", "ffmpeg.exe"),
            os.path.join(app_dir, "ffmpeg", "bin", "ffmpeg"),
            os.path.join(os.path.dirname(app_dir), "ffmpeg", "bin", "ffmpeg.exe"),
            os.path.join(os.path.dirname(app_dir), "ffmpeg", "bin", "ffmpeg"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.ffmpeg_path = path
                self.ffmpeg_status_label.config(text="FFmpeg Ready (Bundled)", fg="green")
                return True
        
        # Check system PATH
        self.ffmpeg_path = shutil.which("ffmpeg")
        if self.ffmpeg_path:
            self.ffmpeg_status_label.config(text="FFmpeg Ready (System)", fg="green")
            return True
        
        # Not found
        self.ffmpeg_status_label.config(text="FFmpeg Not Found - Click Setup", fg="red")
        return False

    def setup_ffmpeg_dialog(self):
        """Show dialog for FFmpeg setup options"""
        dialog = tk.Toplevel(self.window)
        dialog.title("Setup FFmpeg")
        dialog.geometry("420x280")
        dialog.transient(self.window)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (420 // 2)
        y = (dialog.winfo_screenheight() // 2) - (280 // 2)
        dialog.geometry(f"+{x}+{y}")

        title = tk.Label(dialog, text="FFmpeg Setup Required", font=("Arial", 14, "bold"))
        title.pack(pady=15)
        
        info_text = "FFmpeg is required to merge video and audio streams.\nChoose an option below:"
        info = tk.Label(dialog, text=info_text, justify=tk.CENTER, wraplength=380)
        info.pack(pady=10)

        if platform.system() == "Windows":
            btn1 = tk.Button(dialog, text="Auto-Download FFmpeg (Recommended)", 
                     width=38, height=2, bg="#4CAF50", fg="white",
                     command=lambda: [dialog.destroy(), self.download_ffmpeg()])
            btn1.pack(pady=5)
        
        btn2 = tk.Button(dialog, text="Locate FFmpeg Manually", 
                 width=38, height=2,
                 command=lambda: [dialog.destroy(), self.browse_ffmpeg()])
        btn2.pack(pady=5)
        
        btn3 = tk.Button(dialog, text="How to Install FFmpeg", 
                 width=38, height=2,
                 command=self.show_ffmpeg_instructions)
        btn3.pack(pady=5)
        
        btn4 = tk.Button(dialog, text="Cancel", width=38, command=dialog.destroy)
        btn4.pack(pady=5)

    def download_ffmpeg(self):
        """Auto-download FFmpeg (Windows only)"""
        if platform.system() != "Windows":
            msg = "Auto-download is only available for Windows.\nPlease install FFmpeg manually using your package manager."
            messagebox.showinfo("Info", msg)
            return

        msg = "This will download FFmpeg (~100MB) to the application folder.\n\nThis may take a few minutes depending on your internet speed.\n\nDownload and install FFmpeg automatically?"
        response = messagebox.askyesno("Download FFmpeg", msg)
        
        if not response:
            return

        try:
            # Get application directory
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.abspath(__file__))
            
            ffmpeg_dir = os.path.join(app_dir, "ffmpeg")
            
            self.status_label.config(text="Downloading FFmpeg... Please wait (this may take 2-5 minutes)...")
            self.progress["mode"] = "indeterminate"
            self.progress.start(10)
            self.window.update_idletasks()

            # Create ffmpeg directory
            os.makedirs(ffmpeg_dir, exist_ok=True)
            
            # Download FFmpeg
            ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
            zip_path = os.path.join(ffmpeg_dir, "ffmpeg.zip")
            
            urllib.request.urlretrieve(ffmpeg_url, zip_path)
            
            # Extract
            self.status_label.config(text="Extracting FFmpeg...")
            self.window.update_idletasks()
            
            temp_dir = os.path.join(ffmpeg_dir, "temp")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Move to correct location
            extracted_folder = None
            for item in os.listdir(temp_dir):
                if item.startswith("ffmpeg-"):
                    extracted_folder = os.path.join(temp_dir, item)
                    break
            
            if extracted_folder:
                bin_path = os.path.join(extracted_folder, "bin")
                if os.path.exists(bin_path):
                    dest_bin = os.path.join(ffmpeg_dir, "bin")
                    os.makedirs(dest_bin, exist_ok=True)
                    for file in os.listdir(bin_path):
                        shutil.copy2(
                            os.path.join(bin_path, file),
                            os.path.join(dest_bin, file)
                        )
            
            # Cleanup
            self.progress.stop()
            self.progress["mode"] = "determinate"
            shutil.rmtree(temp_dir)
            os.remove(zip_path)
            
            if self.check_ffmpeg():
                messagebox.showinfo("Success", "FFmpeg installed successfully!\n\nYou can now download videos.")
                self.status_label.config(text="FFmpeg ready! Ready to download.", fg="green")
            else:
                raise Exception("FFmpeg extraction failed")
                
        except Exception as e:
            self.progress.stop()
            self.progress["mode"] = "determinate"
            error_msg = f"Failed to download FFmpeg:\n{str(e)}\n\nPlease try manual installation or check your internet connection."
            messagebox.showerror("Error", error_msg)
            self.status_label.config(text="FFmpeg download failed", fg="red")

    def browse_ffmpeg(self):
        """Manually locate FFmpeg executable"""
        file_selected = filedialog.askopenfilename(
            title="Locate ffmpeg.exe",
            filetypes=[("FFmpeg Executable", "ffmpeg.exe"), ("All Files", "*.*")])
        if file_selected and os.path.exists(file_selected):
            self.ffmpeg_path = file_selected
            self.ffmpeg_status_label.config(text="FFmpeg Ready (Custom Path)", fg="green")
            messagebox.showinfo("Success", "FFmpeg path set successfully!\n\nYou can now download videos.")
        elif file_selected:
            messagebox.showerror("Error", "Selected file does not exist.")

    def show_ffmpeg_instructions(self):
        """Show instructions for manual FFmpeg installation"""
        instructions = """Manual FFmpeg Installation Guide:

WINDOWS:
1. Visit: https://www.gyan.dev/ffmpeg/builds/
2. Download "ffmpeg-release-essentials.zip"
3. Extract the ZIP file to a folder
4. Click "Locate FFmpeg Manually" in this app
5. Navigate to the extracted folder -> bin -> select ffmpeg.exe

LINUX:
- Ubuntu/Debian: sudo apt install ffmpeg
- Fedora: sudo dnf install ffmpeg
- Arch: sudo pacman -S ffmpeg

MAC:
- Using Homebrew: brew install ffmpeg

After installation, restart this application or click "Locate FFmpeg Manually".
        """
        msg = tk.Toplevel(self.window)
        msg.title("FFmpeg Installation Guide")
        msg.geometry("500x400")
        msg.transient(self.window)
        
        text_widget = tk.Text(msg, wrap=tk.WORD, padx=15, pady=15, font=("Arial", 10))
        text_widget.pack(expand=True, fill="both")
        text_widget.insert("1.0", instructions.strip())
        text_widget.config(state="disabled")
        
        close_btn = tk.Button(msg, text="Close", command=msg.destroy, width=20)
        close_btn.pack(pady=10)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder_selected)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0%').replace('%', '')
            try:
                percent = float(percent_str)
            except:
                percent = 0
            self.progress["value"] = percent
            speed = d.get('_speed_str', 'N/A')
            eta = d.get('_eta_str', 'N/A')
            status_text = f"Downloading: {percent_str}% | Speed: {speed} | ETA: {eta}"
            self.status_label.config(text=status_text, fg="blue")
            self.window.update_idletasks()
        elif d['status'] == 'finished':
            self.status_label.config(text="Processing and merging video/audio...", fg="orange")
            self.window.update_idletasks()

    def start_download(self):
        url = self.url_entry.get().strip()
        folder = self.folder_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL.")
            return
        if not folder:
            messagebox.showerror("Error", "Please select a download folder.")
            return

        # Check FFmpeg before download
        if not self.ffmpeg_path:
            msg = "FFmpeg is required to download and merge videos.\n\nWould you like to set it up now?"
            response = messagebox.askyesno("FFmpeg Required", msg)
            if response:
                self.setup_ffmpeg_dialog()
            return

        self.progress["value"] = 0
        self.status_label.config(text="Initializing download...", fg="blue")
        self.window.update_idletasks()

        # Format selection
        resolution = self.res_var.get()
        if resolution == "360p":
            fmt = "bestvideo[height<=360]+bestaudio/best[height<=360]"
        elif resolution == "480p":
            fmt = "bestvideo[height<=480]+bestaudio/best[height<=480]"
        elif resolution == "720p":
            fmt = "bestvideo[height<=720]+bestaudio/best[height<=720]"
        elif resolution == "1080p":
            fmt = "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
        else:
            fmt = "bestvideo+bestaudio/best"

        output_template = os.path.join(folder, "%(title)s.%(ext)s")

        # Build options
        ydl_opts = {
            "outtmpl": output_template,
            "format": fmt,
            "merge_output_format": "mp4",
            "progress_hooks": [self.progress_hook],
            "ffmpeg_location": os.path.dirname(self.ffmpeg_path) if self.ffmpeg_path else None,
            "quiet": False,
            "no_warnings": False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'Video')
                title_short = video_title[:50] + "..." if len(video_title) > 50 else video_title
                self.status_label.config(text=f"Downloading: {title_short}", fg="blue")
                self.window.update_idletasks()
                
                ydl.download([url])
            
            self.progress["value"] = 100
            success_msg = f"Download Completed!\n\nSaved to: {folder}"
            messagebox.showinfo("Success", success_msg)
            self.status_label.config(text="Download completed successfully!", fg="green")
        except Exception as e:
            error_msg = f"Download failed:\n\n{str(e)}\n\nPlease check:\n- Valid YouTube URL\n- Internet connection\n- FFmpeg is properly installed"
            messagebox.showerror("Download Error", error_msg)
            self.status_label.config(text="Download failed. Check error message.", fg="red")
            self.progress["value"] = 0


if __name__ == "__main__":
    window = tk.Tk()
    app = DownloadApp(window)
    window.mainloop()

    #thanks