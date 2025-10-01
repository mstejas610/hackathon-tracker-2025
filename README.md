# 🚀 Hackathon Tracker 2025

![Hackathon Tracker](https://img.shields.io/badge/Hackathons-2025-blue?style=for-the-badge&logo=github)
![Status](https://img.shields.io/badge/Status-Live-green?style=for-the-badge)
![Auto-Update](https://img.shields.io/badge/Auto--Update-Every%206h-orange?style=for-the-badge)

**Your one-stop destination for discovering all active and upcoming hackathons in 2025!**

🌐 **Live Website**: [https://mstejas610.github.io/hackathon-tracker-2025/](https://mstejas610.github.io/hackathon-tracker-2025/)

---

## ✨ Features

- 🔄 **Automated Updates**: Data refreshed every 6 hours via GitHub Actions
- 🎯 **Smart Filtering**: Filter by status, type, location, and more
- 🔍 **Powerful Search**: Find hackathons by keywords, tags, or themes
- 📱 **Responsive Design**: Perfect experience on all devices  
- 📊 **Real-time Statistics**: Live counts of active and upcoming events
- 🏷️ **Rich Metadata**: Detailed information including prizes, dates, and registration links
- 🌍 **Multiple Sources**: Aggregates data from DevPost, MLH, and curated events

## 🚀 Quick Start

1. **Visit the Website**: Go to [mstejas610.github.io/hackathon-tracker-2025](https://mstejas610.github.io/hackathon-tracker-2025/)
2. **Browse Hackathons**: View all current and upcoming hackathons
3. **Use Filters**: Narrow down results by your preferences
4. **Register**: Click on any hackathon to register or learn more

## 🛠️ Technical Architecture

### Data Sources
- **DevPost**: Primary hackathon platform with thousands of events
- **Major League Hacking (MLH)**: Official student hackathon organizer
- **Curated List**: Hand-picked high-quality hackathons

### Tech Stack
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python 3.11 with BeautifulSoup4
- **Automation**: GitHub Actions (runs every 6 hours)
- **Hosting**: GitHub Pages
- **Data Format**: JSON

## 📁 Project Structure

```
hackathon-tracker-2025/
├── index.html                 # Main website file
├── data/
│   ├── hackathons.json       # Generated hackathon data
│   └── last_update.txt       # Last update timestamp
├── scripts/
│   └── fetch_hackathons.py   # Data collection script
├── .github/workflows/
│   └── update-hackathons.yml # GitHub Actions workflow
└── README.md                 # This file
```

## 🔧 Development Setup

### Prerequisites
- Python 3.11+
- Git
- GitHub account

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mstejas610/hackathon-tracker-2025.git
   cd hackathon-tracker-2025
   ```

2. **Install Python dependencies**:
   ```bash
   pip install requests beautifulsoup4 lxml python-dateutil pytz
   ```

3. **Run the data fetcher**:
   ```bash
   python scripts/fetch_hackathons.py
   ```

4. **Serve locally**:
   ```bash
   python -m http.server 8000
   ```
   Visit `http://localhost:8000`

## 📊 Data Schema

Each hackathon entry follows this structure:

```json
{
  "title": "AI Global Challenge 2025",
  "description": "Build AI solutions for global problems...",
  "startDate": "2025-02-15",
  "endDate": "2025-02-17",
  "registrationDeadline": "2025-02-10",
  "location": "Online",
  "type": "online|hybrid|in-person",
  "prizePool": "$100,000",
  "status": "active|upcoming|ended",
  "tags": ["AI", "Machine Learning"],
  "registrationUrl": "https://...",
  "websiteUrl": "https://...",
  "organizer": "AI Foundation",
  "source": "DevPost|MLH|Curated"
}
```

## 🔄 Automation Details

### GitHub Actions Workflow
- **Trigger**: Every 6 hours + manual dispatch
- **Process**: 
  1. Fetch data from all sources
  2. Clean and deduplicate
  3. Generate JSON file
  4. Commit changes if data updated
  5. Deploy to GitHub Pages

### Data Refresh Schedule
- **Automatic**: Every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
- **Manual**: Can be triggered from Actions tab
- **On Push**: When scripts are updated

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Adding New Hackathons
1. **Via Issue**: Create an issue with hackathon details
2. **Via PR**: Add to curated list in `fetch_hackathons.py`
3. **Data Source**: Suggest new platforms to scrape

### Bug Reports
Found a bug? [Open an issue](https://github.com/mstejas610/hackathon-tracker-2025/issues) with:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable

## 📱 API Usage

The JSON data is publicly accessible and can be used by other applications:

```javascript
// Fetch current hackathon data
fetch('https://mstejas610.github.io/hackathon-tracker-2025/data/hackathons.json')
  .then(response => response.json())
  .then(hackathons => {
    console.log(`Found ${hackathons.length} hackathons`);
  });
```

## 🌟 Future Enhancements

- [ ] **Email Notifications**: Subscribe to updates
- [ ] **Calendar Integration**: Export to Google Calendar
- [ ] **Advanced Filters**: More granular filtering options
- [ ] **Mobile App**: React Native companion app
- [ ] **Community Features**: User reviews and ratings
- [ ] **RSS Feed**: Subscribe to updates
- [ ] **Dark Mode**: Theme toggle

## 📧 Contact & Support

- **Creator**: [MAREDDY SAI TEJAS](https://github.com/mstejas610)
- **Email**: [Create an Issue](https://github.com/mstejas610/hackathon-tracker-2025/issues) for support

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **DevPost**: For hosting amazing hackathons
- **Major League Hacking**: For fostering the hackathon community  
- **GitHub**: For free hosting and automation
- **Open Source Community**: For inspiration and tools

---

<div align="center">

**⭐ Star this repository if it helped you find your next hackathon! ⭐**

</div>

---

*Built with ❤️ for the developer community | Last updated: October 2025*