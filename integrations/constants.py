# -*- coding: utf-8 -*-
"""Integration constants."""

EVENTBRITE_DOWNLOAD_FREQUENCY_HOURS = 1

# Map EventBrite categories and subcategories to our filters.
EVENTBRITE_CATEGORY_MAPPING = {
    "Music": {
        "id": "103",
        "subcategories": [
            {"id": "3001", "name": "Alternative", "our_filters": ["alternative"]},
            {"id": "3002", "name": "Blues & Jazz", "our_filters": ["blues_and_jazz"]},
            {"id": "3003", "name": "Classical", "our_filters": ["classical"]},
            {"id": "3004", "name": "Country", "our_filters": ["country"]},
            {"id": "3005", "name": "Cultural", "our_filters": ["other_music"]},
            {"id": "3006", "name": "EDM / Electronic", "our_filters": ["electronic"]},
            {"id": "3007", "name": "Folk", "our_filters": ["folk"]},
            {"id": "3008", "name": "Hip Hop / Rap", "our_filters": ["hip_hop_and_rap"]},
            {"id": "3009", "name": "Indie", "our_filters": ["indie"]},
            {"id": "3010", "name": "Latin", "our_filters": ["other_music"]},
            {"id": "3011", "name": "Metal", "our_filters": ["metal"]},
            {"id": "3012", "name": "Opera", "our_filters": ["classical"]},
            {"id": "3013", "name": "Pop", "our_filters": ["pop"]},
            {"id": "3014", "name": "R&B", "our_filters": ["rnb"]},
            {"id": "3015", "name": "Reggae", "our_filters": ["rnb"]},
            {"id": "3016", "name": "Religious/Spiritual", "our_filters": ["other_music"]},
            {"id": "3017", "name": "Rock", "our_filters": ["rock"]},
            {"id": "3018", "name": "Top 40", "our_filters": ["pop"]},
            {"id": "3019", "name": "Acoustic", "our_filters": ["acoustic"]},
            {"id": "3020", "name": "Americana", "our_filters": ["other_music"]},
            {"id": "3021", "name": "Bluegrass", "our_filters": ["other_music"]},
            {"id": "3022", "name": "Blues", "our_filters": ["blues_and_jazz"]},
            {"id": "3023", "name": "DJ/Dance", "our_filters": ["electronic"]},
            {"id": "3024", "name": "EDM", "our_filters": ["electronic"]},
            {"id": "3025", "name": "Electronic", "our_filters": ["electronic"]},
            {"id": "3026", "name": "Experimental", "our_filters": ["other_music"]},
            {"id": "3027", "name": "Jazz", "our_filters": ["blues_and_jazz"]},
            {"id": "3028", "name": "Psychedelic", "our_filters": ["electronic"]},
            {"id": "3029", "name": "Punk/Hardcore", "our_filters": ["punk"]},
            {"id": "3030", "name": "Singer/Songwriter", "our_filters": ["other_music"]},
            {"id": "3031", "name": "World", "our_filters": ["other_music"]},
            {"id": "3999", "name": "Other", "our_filters": ["other_music"]},
        ],
        "our_filters": ["other_music"],
    },
    "Business & Professional": {
        "id": "101",
        "subcategories": [
            {"id": "1001", "name": "Startups & Small Business", "our_filters": ["business"]},
            {"id": "1002", "name": "Finance", "our_filters": ["business"]},
            {"id": "1003", "name": "Environment & Sustainability", "our_filters": ["business"]},
            {"id": "1004", "name": "Educators", "our_filters": ["business"]},
            {"id": "1005", "name": "Real Estate", "our_filters": ["business"]},
            {"id": "1006", "name": "Non Profit & NGOs", "our_filters": ["business"]},
            {"id": "1007", "name": "Sales & Marketing", "our_filters": ["business"]},
            {"id": "1008", "name": "Media", "our_filters": ["business"]},
            {"id": "1009", "name": "Design", "our_filters": ["business"]},
            {"id": "1010", "name": "Career", "our_filters": ["business"]},
            {"id": "1011", "name": "Investment", "our_filters": ["business"]},
            {"id": "1999", "name": "Other", "our_filters": ["business"]},
        ],
        "our_filters": ["business"],
    },
    "Food & Drink": {
        "id": "110",
        "subcategories": [
            {"id": "10001", "name": "Beer", "our_filters": []},
            {"id": "10002", "name": "Wine", "our_filters": []},
            {"id": "10003", "name": "Food", "our_filters": []},
            {"id": "10004", "name": "Spirits", "our_filters": []},
            {"id": "10999", "name": "Other", "our_filters": []},
        ],
        "our_filters": ["other_food_and_drink"],
    },
    "Community & Culture": {
        "id": "113",
        "subcategories": [
            {"id": "13001", "name": "State", "our_filters": ["culture"]},
            {"id": "13002", "name": "County", "our_filters": ["culture"]},
            {"id": "13003", "name": "City/Town", "our_filters": ["culture"]},
            {"id": "13004", "name": "LGBT", "our_filters": ["culture"]},
            {"id": "13005", "name": "Medieval", "our_filters": ["culture"]},
            {"id": "13006", "name": "Renaissance", "our_filters": ["culture"]},
            {"id": "13007", "name": "Heritage", "our_filters": ["culture"]},
            {"id": "13008", "name": "Nationality", "our_filters": ["culture"]},
            {"id": "13009", "name": "Language", "our_filters": ["culture"]},
            {"id": "13010", "name": "Historic", "our_filters": ["culture"]},
            {"id": "13999", "name": "Other", "our_filters": ["culture"]},
        ],
        "our_filters": ["culture"],
    },
    "Performing & Visual Arts": {
        "id": "105",
        "subcategories": [
            {"id": "5001", "name": "Theatre", "our_filters": ["theatre"]},
            {"id": "5002", "name": "Musical", "our_filters": ["theatre"]},
            {"id": "5003", "name": "Ballet", "our_filters": ["theatre", "other_arts"]},
            {"id": "5004", "name": "Dance", "our_filters": ["theatre", "other_arts"]},
            {"id": "5005", "name": "Opera", "our_filters": ["theatre", "other_arts"]},
            {
                "id": "5006",
                "name": "Orchestra",
                "our_filters": ["theatre", "other_arts", "classical"],
            },
            {"id": "5007", "name": "Craft", "our_filters": ["arts_and_crafts"]},
            {"id": "5008", "name": "Fine Art", "our_filters": ["arts_and_crafts", "other_arts"]},
            {
                "id": "5009",
                "name": "Literary Arts",
                "our_filters": ["arts_and_crafts", "other_arts"],
            },
            {"id": "5010", "name": "Comedy", "our_filters": ["comedy"]},
            {"id": "5011", "name": "Sculpture", "our_filters": ["arts_and_crafts"]},
            {"id": "5012", "name": "Painting", "our_filters": ["arts_and_crafts"]},
            {"id": "5013", "name": "Design", "our_filters": ["arts_and_crafts"]},
            {"id": "5014", "name": "Jewelry", "our_filters": ["arts_and_crafts", "fashion"]},
            {"id": "5999", "name": "Other", "our_filters": ["other_arts"]},
        ],
        "our_filters": ["other_arts"],
    },
    "Film, Media & Entertainment": {
        "id": "104",
        "subcategories": [
            {"id": "4001", "name": "TV", "our_filters": ["cinema_and_film"]},
            {"id": "4002", "name": "Film", "our_filters": ["cinema_and_film"]},
            {"id": "4003", "name": "Anime", "our_filters": ["cinema_and_film", "other_hobbies"]},
            {"id": "4004", "name": "Gaming", "our_filters": ["games"]},
            {"id": "4005", "name": "Comics", "our_filters": ["other_hobbies"]},
            {"id": "4006", "name": "Adult", "our_filters": ["other_hobbies"]},
            {"id": "4007", "name": "Comedy", "our_filters": ["comedy"]},
            {"id": "4999", "name": "Other", "our_filters": ["other_hobbies"]},
        ],
        "our_filters": ["cinema_and_film"],
    },
    "Sports & Fitness": {
        "id": "108",
        "subcategories": [
            {"id": "8001", "name": "Running", "our_filters": ["exercise_and_fitness"]},
            {"id": "8002", "name": "Walking", "our_filters": ["exercise_and_fitness"]},
            {"id": "8003", "name": "Cycling", "our_filters": ["cycling"]},
            {"id": "8004", "name": "Mountain Biking", "our_filters": ["cycling"]},
            {"id": "8005", "name": "Obstacles", "our_filters": ["exercise_and_fitness"]},
            {"id": "8006", "name": "Basketball", "our_filters": ["team_sports", "ball_games"]},
            {"id": "8007", "name": "Football", "our_filters": ["team_sports", "ball_games"]},
            {"id": "8008", "name": "Baseball", "our_filters": ["team_sports", "ball_games"]},
            {"id": "8009", "name": "Soccer", "our_filters": ["team_sports", "ball_games"]},
            {"id": "8010", "name": "Golf", "our_filters": ["ball_games"]},
            {"id": "8011", "name": "Volleyball", "our_filters": ["team_sports", "ball_games"]},
            {"id": "8012", "name": "Tennis", "our_filters": ["team_sports", "ball_games"]},
            {"id": "8013", "name": "Swimming & Water Sports", "our_filters": ["water_sports"]},
            {"id": "8014", "name": "Hockey", "our_filters": ["team_sports", "ball_games"]},
            {"id": "8015", "name": "Motorsports", "our_filters": ["motorsport"]},
            {"id": "8016", "name": "Fighting & Martial Arts", "our_filters": ["martial_arts"]},
            {"id": "8017", "name": "Snow Sports", "our_filters": ["winter_sports"]},
            {"id": "8018", "name": "Rugby", "our_filters": ["team_sports", "ball_games"]},
            {"id": "8019", "name": "Yoga", "our_filters": ["exercise_and_fitness"]},
            {"id": "8020", "name": "Exercise", "our_filters": ["exercise_and_fitness"]},
            {"id": "8021", "name": "Softball", "our_filters": ["team_sports", "ball_games"]},
            {"id": "8022", "name": "Wrestling", "our_filters": ["other_sports"]},
            {"id": "8023", "name": "Lacrosse", "our_filters": ["team_sports", "ball_games"]},
            {"id": "8024", "name": "Cheer", "our_filters": ["exercise_and_fitness"]},
            {"id": "8025", "name": "Camps", "our_filters": ["exercise_and_fitness"]},
            {"id": "8026", "name": "Weightlifting", "our_filters": ["exercise_and_fitness"]},
            {"id": "8027", "name": "Track & Field", "our_filters": ["exercise_and_fitness"]},
            {"id": "8999", "name": "Other", "our_filters": ["other_sports"]},
        ],
        "our_filters": ["other_sports"],
    },
    "Health & Wellness": {
        "id": "107",
        "subcategories": [
            {"id": "7001", "name": "Personal health", "our_filters": ["wellbeing"]},
            {"id": "7002", "name": "Mental health", "our_filters": ["wellbeing"]},
            {"id": "7003", "name": "Medical", "our_filters": ["wellbeing"]},
            {"id": "7004", "name": "Spa", "our_filters": ["wellbeing"]},
            {"id": "7005", "name": "Yoga", "our_filters": ["wellbeing", "exercise_and_fitness"]},
            {"id": "7999", "name": "Other", "our_filters": ["wellbeing"]},
        ],
        "our_filters": ["wellbeing"],
    },
    "Science & Technology": {
        "id": "102",
        "subcategories": [
            {"id": "2001", "name": "Medicine", "our_filters": ["science_and_tech"]},
            {"id": "2002", "name": "Science", "our_filters": ["science_and_tech"]},
            {"id": "2003", "name": "Biotech", "our_filters": ["science_and_tech"]},
            {"id": "2004", "name": "High Tech", "our_filters": ["science_and_tech"]},
            {"id": "2005", "name": "Mobile", "our_filters": ["science_and_tech"]},
            {"id": "2006", "name": "Social Media", "our_filters": ["science_and_tech"]},
            {"id": "2007", "name": "Robotics", "our_filters": ["science_and_tech"]},
            {"id": "2999", "name": "Other", "our_filters": ["science_and_tech"]},
        ],
        "our_filters": ["science_and_tech"],
    },
    "Travel & Outdoor": {
        "id": "109",
        "subcategories": [
            {"id": "9001", "name": "Hiking", "our_filters": ["exercise_and_fitness", "outdoor"]},
            {
                "id": "9002",
                "name": "Rafting",
                "our_filters": ["exercise_and_fitness", "outdoor", "water_sports"],
            },
            {
                "id": "9003",
                "name": "Kayaking",
                "our_filters": ["exercise_and_fitness", "outdoor", "water_sports"],
            },
            {
                "id": "9004",
                "name": "Canoeing",
                "our_filters": ["exercise_and_fitness", "outdoor", "water_sports"],
            },
            {"id": "9005", "name": "Climbing", "our_filters": ["exercise_and_fitness", "outdoor"]},
            {"id": "9006", "name": "Travel", "our_filters": ["travel", "outdoor"]},
            {"id": "9999", "name": "Other", "our_filters": ["travel", "outdoor"]},
        ],
        "our_filters": ["travel", "outdoor"],
    },
    "Charity & Causes": {
        "id": "111",
        "subcategories": [
            {"id": "11001", "name": "Animal Welfare", "our_filters": ["charity_and_causes"]},
            {"id": "11002", "name": "Environment", "our_filters": ["charity_and_causes"]},
            {"id": "11003", "name": "Healthcare", "our_filters": ["charity_and_causes"]},
            {"id": "11004", "name": "Human Rights", "our_filters": ["charity_and_causes"]},
            {"id": "11005", "name": "International Aid", "our_filters": ["charity_and_causes"]},
            {"id": "11006", "name": "Poverty", "our_filters": ["charity_and_causes"]},
            {"id": "11007", "name": "Disaster Relief", "our_filters": ["charity_and_causes"]},
            {"id": "11008", "name": "Education", "our_filters": ["charity_and_causes"]},
            {"id": "11999", "name": "Other", "our_filters": ["charity_and_causes"]},
        ],
        "our_filters": ["charity_and_causes"],
    },
    "Religion & Spirituality": {
        "id": "114",
        "subcategories": [
            {"id": "14001", "name": "Christianity", "our_filters": ["spirituality"]},
            {"id": "14002", "name": "Judaism", "our_filters": ["spirituality"]},
            {"id": "14003", "name": "Islam", "our_filters": ["spirituality"]},
            {"id": "14004", "name": "Mormonism", "our_filters": ["spirituality"]},
            {"id": "14005", "name": "Buddhism", "our_filters": ["spirituality"]},
            {"id": "14006", "name": "Sikhism", "our_filters": ["spirituality"]},
            {"id": "14007", "name": "Eastern Religion", "our_filters": ["spirituality"]},
            {"id": "14008", "name": "Mysticism and Occult", "our_filters": ["spirituality"]},
            {"id": "14009", "name": "New Age", "our_filters": ["spirituality"]},
            {"id": "14010", "name": "Atheism", "our_filters": ["spirituality"]},
            {"id": "14011", "name": "Agnosticism", "our_filters": ["spirituality"]},
            {"id": "14012", "name": "Unaffiliated", "our_filters": ["spirituality"]},
            {"id": "14013", "name": "Hinduism", "our_filters": ["spirituality"]},
            {"id": "14014", "name": "Folk Religions", "our_filters": ["spirituality"]},
            {"id": "14015", "name": "Shintoism", "our_filters": ["spirituality"]},
            {"id": "14099", "name": "Other", "our_filters": ["spirituality"]},
        ],
        "our_filters": ["spirituality"],
    },
    "Family & Education": {
        "id": "115",
        "subcategories": [
            {
                "id": "15001",
                "name": "Education",
                "our_filters": ["educational", "parenting_and_family"],
            },
            {
                "id": "15002",
                "name": "Alumni",
                "our_filters": ["educational", "parenting_and_family"],
            },
            {"id": "15003", "name": "Parenting", "our_filters": ["parenting_and_family"]},
            {"id": "15004", "name": "Baby", "our_filters": ["parenting_and_family"]},
            {"id": "15005", "name": "Children & Youth ", "our_filters": ["parenting_and_family"]},
            {
                "id": "15006",
                "name": "Parents Association",
                "our_filters": ["educational", "parenting_and_family"],
            },
            {"id": "15007", "name": "Reunion", "our_filters": ["parenting_and_family"]},
            {"id": "15008", "name": "Senior Citizen", "our_filters": ["parenting_and_family"]},
            {"id": "15999", "name": "Other", "our_filters": ["parenting_and_family"]},
        ],
        "our_filters": ["parenting_and_family"],
    },
    "Seasonal & Holiday": {
        "id": "116",
        "subcategories": [
            {"id": "16001", "name": "St Patricks Day", "our_filters": ["seasonal_and_holiday"]},
            {"id": "16002", "name": "Easter", "our_filters": ["seasonal_and_holiday"]},
            {"id": "16003", "name": "Independence Day", "our_filters": ["seasonal_and_holiday"]},
            {"id": "16004", "name": "Halloween/Haunt", "our_filters": ["seasonal_and_holiday"]},
            {"id": "16005", "name": "Thanksgiving", "our_filters": ["seasonal_and_holiday"]},
            {"id": "16006", "name": "Christmas", "our_filters": ["seasonal_and_holiday"]},
            {"id": "16007", "name": "Channukah", "our_filters": ["seasonal_and_holiday"]},
            {"id": "16008", "name": "Fall events", "our_filters": ["seasonal_and_holiday"]},
            {"id": "16009", "name": "New Years Eve", "our_filters": ["seasonal_and_holiday"]},
            {"id": "16999", "name": "Other", "our_filters": ["seasonal_and_holiday"]},
        ],
        "our_filters": ["seasonal_and_holiday"],
    },
    "Government & Politics": {
        "id": "112",
        "subcategories": [
            {"id": "12001", "name": "Republican Party", "our_filters": ["politics"]},
            {"id": "12002", "name": "Democratic Party", "our_filters": ["politics"]},
            {"id": "12003", "name": "Other Party", "our_filters": ["politics"]},
            {"id": "12004", "name": "Non-partisan", "our_filters": ["politics"]},
            {"id": "12005", "name": "Federal Government", "our_filters": ["politics"]},
            {"id": "12006", "name": "State Government", "our_filters": ["politics"]},
            {"id": "12007", "name": "County/Municipal Government ", "our_filters": ["politics"]},
            {"id": "12008", "name": "Military", "our_filters": ["politics"]},
            {"id": "12009", "name": "International Affairs", "our_filters": ["politics"]},
            {"id": "12010", "name": "National Security", "our_filters": ["politics"]},
            {"id": "12999", "name": "Other", "our_filters": ["politics"]},
        ],
        "our_filters": ["politics"],
    },
    "Fashion & Beauty": {
        "id": "106",
        "subcategories": [
            {"id": "6001", "name": "Fashion", "our_filters": ["fashion"]},
            {"id": "6002", "name": "Accessories", "our_filters": ["fashion"]},
            {"id": "6003", "name": "Bridal", "our_filters": ["fashion", "wedding"]},
            {"id": "6004", "name": "Beauty", "our_filters": ["fashion"]},
            {"id": "6999", "name": "Other", "our_filters": ["fashion"]},
        ],
        "our_filters": ["fashion"],
    },
    "Home & Lifestyle": {
        "id": "117",
        "subcategories": [
            {"id": "17001", "name": "Dating", "our_filters": ["dating"]},
            {
                "id": "17002",
                "name": "Pets & Animals",
                "our_filters": ["home_and_lifestyle", "pets"],
            },
            {"id": "17003", "name": "Home & Garden", "our_filters": ["home_and_lifestyle"]},
            {"id": "17999", "name": "Other", "our_filters": ["home_and_lifestyle"]},
        ],
        "our_filters": ["home_and_lifestyle"],
    },
    "Auto, Boat & Air": {
        "id": "118",
        "subcategories": [
            {
                "id": "18001",
                "name": "Auto",
                "our_filters": ["vehicles_and_transport", "motorsport"],
            },
            {
                "id": "18002",
                "name": "Motorcycle/ATV",
                "our_filters": ["vehicles_and_transport", "motorsport"],
            },
            {"id": "18003", "name": "Boat", "our_filters": ["vehicles_and_transport"]},
            {"id": "18004", "name": "Air", "our_filters": ["vehicles_and_transport", "motorsport"]},
            {
                "id": "18999",
                "name": "Other",
                "our_filters": ["vehicles_and_transport", "motorsport"],
            },
        ],
        "our_filters": ["vehicles_and_transport"],
    },
    "Hobbies & Special Interest": {
        "id": "119",
        "subcategories": [
            {"id": "19001", "name": "Anime/Comics", "our_filters": ["other_hobbies"]},
            {"id": "19002", "name": "Gaming", "our_filters": ["games"]},
            {"id": "19003", "name": "DIY", "our_filters": ["other_hobbies", "home_and_lifestyle"]},
            {"id": "19004", "name": "Photography", "our_filters": ["other_hobbies"]},
            {
                "id": "19005",
                "name": "Knitting",
                "our_filters": ["other_hobbies", "arts_and_crafts"],
            },
            {"id": "19006", "name": "Books", "our_filters": ["other_hobbies"]},
            {"id": "19007", "name": "Adult", "our_filters": ["other_hobbies"]},
            {"id": "19008", "name": "Drawing & Painting", "our_filters": ["arts_and_crafts"]},
            {"id": "19999", "name": "Other", "our_filters": ["other_hobbies"]},
        ],
        "our_filters": ["other_hobbies"],
    },
    "Other": {"id": "199", "subcategories": [], "our_filters": []},
    "School Activities": {
        "id": "120",
        "subcategories": [
            {"id": "20001", "name": "Dinner", "our_filters": ["educational"]},
            {
                "id": "20002",
                "name": "Fund Raiser",
                "our_filters": ["educational", "charity_and_causes"],
            },
            {"id": "20003", "name": "Raffle", "our_filters": ["educational", "charity_and_causes"]},
            {
                "id": "20004",
                "name": "After School Care",
                "our_filters": ["educational", "parenting_and_family"],
            },
            {"id": "20005", "name": "Parking", "our_filters": ["educational"]},
            {"id": "20006", "name": "Public Speaker", "our_filters": ["educational"]},
        ],
        "our_filters": ["educational"],
    },
}