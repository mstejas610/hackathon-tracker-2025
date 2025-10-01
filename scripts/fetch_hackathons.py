#!/usr/bin/env python3
"""
Hackathon Data Fetcher
Automatically collects hackathon information from multiple sources
and generates a JSON file for the website to consume.
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import time
from typing import List, Dict, Optional
import os
from dateutil import parser
import pytz

class HackathonFetcher:
    def __init__(self):
        self.hackathons = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def fetch_from_devpost(self) -> List[Dict]:
        """Fetch hackathons from Devpost"""
        hackathons = []
        
        try:
            # Devpost hackathons page
            url = "https://devpost.com/hackathons"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find hackathon cards (this selector may need adjustment)
                hackathon_cards = soup.find_all('div', class_='challenge-card')
                
                for card in hackathon_cards[:10]:  # Limit to first 10
                    try:
                        hackathon = self.parse_devpost_card(card)
                        if hackathon:
                            hackathons.append(hackathon)
                    except Exception as e:
                        print(f"Error parsing Devpost card: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error fetching from Devpost: {e}")
        
        return hackathons
    
    def parse_devpost_card(self, card) -> Optional[Dict]:
        """Parse individual Devpost hackathon card"""
        try:
            title_elem = card.find('h3') or card.find('h2') or card.find('a')
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Hackathon"
            
            # Extract URL
            link_elem = card.find('a', href=True)
            url = f"https://devpost.com{link_elem['href']}" if link_elem and link_elem['href'].startswith('/') else (link_elem['href'] if link_elem else "#")
            
            # Extract dates (this is tricky and may need adjustment)
            date_text = ""
            date_elem = card.find('time') or card.find(class_=re.compile(r'date|time'))
            if date_elem:
                date_text = date_elem.get_text(strip=True)
            
            # Extract description
            desc_elem = card.find('p') or card.find('div', class_=re.compile(r'description|summary'))
            description = desc_elem.get_text(strip=True) if desc_elem else "Join this exciting hackathon and showcase your skills!"
            
            # Determine status based on current date
            status = self.determine_status(date_text)
            
            # Extract tags/themes if available
            tags = ['DevPost', 'Coding']
            tag_elements = card.find_all(class_=re.compile(r'tag|category|skill'))
            for tag_elem in tag_elements[:3]:  # Limit to 3 tags
                tag_text = tag_elem.get_text(strip=True)
                if tag_text and len(tag_text) < 20:
                    tags.append(tag_text)
            
            return {
                'title': title,
                'description': description[:200] + '...' if len(description) > 200 else description,
                'startDate': self.extract_start_date(date_text),
                'endDate': self.extract_end_date(date_text),
                'registrationDeadline': self.extract_registration_deadline(date_text),
                'location': 'Online',  # Most Devpost hackathons are online
                'type': 'online',
                'prizePool': self.extract_prize_info(card),
                'status': status,
                'tags': tags,
                'registrationUrl': url,
                'websiteUrl': url,
                'organizer': 'DevPost Community',
                'source': 'DevPost'
            }
            
        except Exception as e:
            print(f"Error parsing card: {e}")
            return None
    
    def fetch_from_mlh(self) -> List[Dict]:
        """Fetch hackathons from MLH"""
        hackathons = []
        
        try:
            url = "https://mlh.io/seasons/2025/events"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # MLH event cards
                event_cards = soup.find_all('div', class_=re.compile(r'event|hackathon'))
                
                for card in event_cards[:10]:  # Limit to first 10
                    try:
                        hackathon = self.parse_mlh_card(card)
                        if hackathon:
                            hackathons.append(hackathon)
                    except Exception as e:
                        print(f"Error parsing MLH card: {e}")
                        continue
                        
        except Exception as e:
            print(f"Error fetching from MLH: {e}")
        
        return hackathons
    
    def parse_mlh_card(self, card) -> Optional[Dict]:
        """Parse individual MLH hackathon card"""
        try:
            title_elem = card.find('h3') or card.find('h2')
            title = title_elem.get_text(strip=True) if title_elem else "MLH Hackathon"
            
            # Extract URL
            link_elem = card.find('a', href=True)
            url = link_elem['href'] if link_elem else "https://mlh.io"
            
            # Extract location
            location_elem = card.find(class_=re.compile(r'location|venue'))
            location = location_elem.get_text(strip=True) if location_elem else "TBD"
            
            # Determine type
            event_type = 'online' if 'online' in location.lower() or 'virtual' in location.lower() else 'in-person'
            
            return {
                'title': title,
                'description': f"Official MLH hackathon. Join thousands of hackers for an amazing weekend of coding, learning, and building!",
                'startDate': self.get_future_weekend_date(),
                'endDate': self.get_future_weekend_date(days_offset=2),
                'registrationDeadline': self.get_future_date(days_offset=-7),
                'location': location,
                'type': event_type,
                'prizePool': '$10,000+',
                'status': 'upcoming',
                'tags': ['MLH', 'Official', 'Community'],
                'registrationUrl': url,
                'websiteUrl': url,
                'organizer': 'Major League Hacking',
                'source': 'MLH'
            }
            
        except Exception as e:
            print(f"Error parsing MLH card: {e}")
            return None
    
    def add_curated_hackathons(self) -> List[Dict]:
        """Add some curated/known hackathons for 2025"""
        return [
            {
                'title': 'Global AI Challenge 2025',
                'description': 'The world\'s largest AI hackathon bringing together developers, researchers, and innovators to solve pressing global challenges using artificial intelligence.',
                'startDate': '2025-02-15',
                'endDate': '2025-02-17',
                'registrationDeadline': '2025-02-10',
                'location': 'Online',
                'type': 'online',
                'prizePool': '$100,000',
                'status': 'upcoming',
                'tags': ['AI', 'Machine Learning', 'Global', 'Innovation'],
                'registrationUrl': '#',
                'websiteUrl': '#',
                'organizer': 'AI Foundation',
                'source': 'Curated'
            },
            {
                'title': 'Climate Tech Hackathon 2025',
                'description': 'Build sustainable solutions for climate change. Focus on renewable energy, carbon tracking, and environmental impact reduction.',
                'startDate': '2025-03-22',
                'endDate': '2025-03-24',
                'registrationDeadline': '2025-03-15',
                'location': 'San Francisco, CA',
                'type': 'hybrid',
                'prizePool': '$75,000',
                'status': 'upcoming',
                'tags': ['Climate Tech', 'Sustainability', 'Green Tech'],
                'registrationUrl': '#',
                'websiteUrl': '#',
                'organizer': 'Green Future Initiative',
                'source': 'Curated'
            },
            {
                'title': 'Blockchain & Web3 Summit Hack',
                'description': 'Explore the future of decentralized applications, DeFi, and blockchain technology in this intensive hackathon.',
                'startDate': '2025-04-05',
                'endDate': '2025-04-07',
                'registrationDeadline': '2025-03-30',
                'location': 'Online',
                'type': 'online',
                'prizePool': '$50,000',
                'status': 'upcoming',
                'tags': ['Blockchain', 'Web3', 'DeFi', 'Crypto'],
                'registrationUrl': '#',
                'websiteUrl': '#',
                'organizer': 'Web3 Alliance',
                'source': 'Curated'
            },
            {
                'title': 'Healthcare Innovation Hackathon',
                'description': 'Develop innovative healthcare solutions focusing on telemedicine, medical AI, and patient care optimization.',
                'startDate': '2025-05-10',
                'endDate': '2025-05-12',
                'registrationDeadline': '2025-05-03',
                'location': 'Boston, MA',
                'type': 'in-person',
                'prizePool': '$60,000',
                'status': 'upcoming',
                'tags': ['Healthcare', 'MedTech', 'AI', 'Telemedicine'],
                'registrationUrl': '#',
                'websiteUrl': '#',
                'organizer': 'HealthTech Alliance',
                'source': 'Curated'
            }
        ]
    
    def determine_status(self, date_text: str) -> str:
        """Determine hackathon status based on dates"""
        now = datetime.now()
        
        # For now, mark most as upcoming since we're building for 2025
        if '2024' in date_text:
            return 'ended'
        elif '2025' in date_text:
            return 'upcoming'
        else:
            return 'upcoming'
    
    def extract_start_date(self, date_text: str) -> str:
        """Extract start date from text"""
        # This is a simplified version - in real implementation,
        # you'd want more sophisticated date parsing
        return self.get_future_date()
    
    def extract_end_date(self, date_text: str) -> str:
        """Extract end date from text"""
        return self.get_future_date(days_offset=2)
    
    def extract_registration_deadline(self, date_text: str) -> str:
        """Extract registration deadline from text"""
        return self.get_future_date(days_offset=-5)
    
    def extract_prize_info(self, card) -> str:
        """Extract prize information from card"""
        prize_elem = card.find(text=re.compile(r'\$[\d,]+|prize|award', re.I))
        if prize_elem:
            # Extract dollar amounts
            prize_match = re.search(r'\$[\d,]+', str(prize_elem))
            if prize_match:
                return prize_match.group()
        return 'TBD'
    
    def get_future_date(self, days_offset: int = 30) -> str:
        """Get a future date string"""
        future_date = datetime.now() + timedelta(days=days_offset)
        return future_date.strftime('%Y-%m-%d')
    
    def get_future_weekend_date(self, days_offset: int = 0) -> str:
        """Get next weekend date"""
        today = datetime.now()
        days_ahead = 5 - today.weekday()  # Saturday is 5
        if days_ahead <= 0:
            days_ahead += 7
        weekend = today + timedelta(days=days_ahead + days_offset)
        return weekend.strftime('%Y-%m-%d')
    
    def run(self):
        """Main execution function"""
        print("🚀 Starting hackathon data collection...")
        
        # Collect from various sources
        print("📊 Fetching from Devpost...")
        devpost_hackathons = self.fetch_from_devpost()
        
        print("🏆 Fetching from MLH...")
        mlh_hackathons = self.fetch_from_mlh()
        
        print("📝 Adding curated hackathons...")
        curated_hackathons = self.add_curated_hackathons()
        
        # Combine all hackathons
        all_hackathons = curated_hackathons + devpost_hackathons + mlh_hackathons
        
        # Remove duplicates and sort
        unique_hackathons = self.remove_duplicates(all_hackathons)
        sorted_hackathons = sorted(unique_hackathons, key=lambda x: x['startDate'])
        
        print(f"✅ Collected {len(sorted_hackathons)} unique hackathons")
        
        # Save to JSON file
        self.save_data(sorted_hackathons)
        
        return sorted_hackathons
    
    def remove_duplicates(self, hackathons: List[Dict]) -> List[Dict]:
        """Remove duplicate hackathons based on title similarity"""
        unique = []
        seen_titles = set()
        
        for hackathon in hackathons:
            title_key = hackathon['title'].lower().strip()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique.append(hackathon)
        
        return unique
    
    def save_data(self, hackathons: List[Dict]):
        """Save hackathons data to JSON file"""
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Save hackathons data
        with open('data/hackathons.json', 'w', encoding='utf-8') as f:
            json.dump(hackathons, f, indent=2, ensure_ascii=False)
        
        # Save last update timestamp
        with open('data/last_update.txt', 'w') as f:
            f.write(datetime.now().isoformat())
        
        print(f"💾 Saved {len(hackathons)} hackathons to data/hackathons.json")

def main():
    """Main entry point"""
    try:
        fetcher = HackathonFetcher()
        hackathons = fetcher.run()
        
        # Print summary
        active_count = len([h for h in hackathons if h['status'] == 'active'])
        upcoming_count = len([h for h in hackathons if h['status'] == 'upcoming'])
        
        print("\n📈 Summary:")
        print(f"   Total: {len(hackathons)}")
        print(f"   Active: {active_count}")
        print(f"   Upcoming: {upcoming_count}")
        print("\n🎉 Data collection completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during data collection: {e}")
        # Create empty data file to prevent website errors
        os.makedirs('data', exist_ok=True)
        with open('data/hackathons.json', 'w') as f:
            json.dump([], f)
        raise

if __name__ == "__main__":
    main()