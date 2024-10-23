# video_generator





## TextFile View Enhancements
- **Created a dedicated view for processing video files** using Django's `call_command`, ensuring better separation of concerns.

## Text to Speech Conversion
- **Improved audio file handling**: Integrated Django's `FileField` for saving generated audio files, enhancing file management.
- **Timestamping**: Utilized timestamps for generating unique filenames for audio and video files to avoid overwrites.

## Forms
- **TextFileForm**: Added resolution options with choices for better user experience during file uploads.

## Decorators
- **Custom decorators for credit checks**: Added decorators to ensure users have enough credits and own the associated `TextFile`, improving access control.

## Color Converter
- **Implemented a robust color input handling function**: Added support for multiple color formats (hex, RGB, RGBA, HSL) with normalization for better color management.

## URL Patterns
- **Organized URL patterns**: Ensured clear routing for video processing and downloading functionality, improving maintainability.

## Background Music Model
- **Enhanced the BackgroundMusic model**: Improved file upload paths for uniqueness, ensuring that each background music file is correctly associated with its `TextFile`.

## Audio Application
- **Improved audio file upload handling**: Used UUID for generating unique file names to prevent conflicts during uploads.

## Miscellaneous Improvements
- **Error handling**: Improved error messages and responses for better user feedback during various operations.
- **Code organization**: Ensured consistent code structure and naming conventions across different modules to enhance readability and maintainability.
