from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
from models import User, ClubProfile, SponsorProfile, Event, Message, SponsorInterest
from forms import LoginForm, RegistrationForm, ClubProfileForm, SponsorProfileForm, EventForm, MessageForm, SearchForm
from ai_matcher import ai_matcher
from datetime import datetime

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'error')
            return render_template('register.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'error')
            return render_template('register.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            user_type=form.user_type.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please complete your profile.', 'success')
        login_user(user)
        
        # Redirect to profile setup
        if user.user_type == 'club':
            return redirect(url_for('create_club_profile'))
        else:
            return redirect(url_for('create_sponsor_profile'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    if current_user.user_type == 'club':
        return redirect(url_for('club_dashboard'))
    else:
        return redirect(url_for('sponsor_dashboard'))

@app.route('/club/dashboard')
@login_required
def club_dashboard():
    """Club dashboard"""
    if current_user.user_type != 'club':
        flash('Access denied. Clubs only.', 'error')
        return redirect(url_for('index'))
    
    # Get or create club profile
    club_profile = current_user.club_profile
    if not club_profile:
        flash('Please complete your club profile first.', 'warning')
        return redirect(url_for('create_club_profile'))
    
    # Get club events
    events = Event.query.filter_by(club_id=club_profile.id).all()
    
    # Get AI recommendations for events
    recommendations = []
    for event in events[:3]:  # Limit to 3 events for dashboard
        event_recommendations = ai_matcher.get_sponsor_recommendations(event, limit=3)
        recommendations.append({
            'event': event,
            'sponsors': event_recommendations
        })
    
    # Get recent messages
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.created_at.desc()).limit(5).all()
    
    return render_template('club_dashboard.html', 
                         club_profile=club_profile, 
                         events=events, 
                         recommendations=recommendations,
                         messages=messages)

@app.route('/sponsor/dashboard')
@login_required
def sponsor_dashboard():
    """Sponsor dashboard"""
    if current_user.user_type != 'sponsor':
        flash('Access denied. Sponsors only.', 'error')
        return redirect(url_for('index'))
    
    # Get or create sponsor profile
    sponsor_profile = current_user.sponsor_profile
    if not sponsor_profile:
        flash('Please complete your sponsor profile first.', 'warning')
        return redirect(url_for('create_sponsor_profile'))
    
    # Get AI recommendations
    recommendations = ai_matcher.get_event_recommendations(sponsor_profile, limit=5)
    
    # Get sponsor interests
    interests = SponsorInterest.query.filter_by(sponsor_id=sponsor_profile.id).order_by(SponsorInterest.created_at.desc()).limit(5).all()
    
    # Get recent messages
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.created_at.desc()).limit(5).all()
    
    return render_template('sponsor_dashboard.html', 
                         sponsor_profile=sponsor_profile, 
                         recommendations=recommendations,
                         interests=interests,
                         messages=messages)

@app.route('/club/profile', methods=['GET', 'POST'])
@login_required
def create_club_profile():
    """Create or edit club profile"""
    if current_user.user_type != 'club':
        flash('Access denied. Clubs only.', 'error')
        return redirect(url_for('index'))
    
    form = ClubProfileForm()
    club_profile = current_user.club_profile
    
    if form.validate_on_submit():
        if club_profile:
            # Update existing profile
            club_profile.club_name = form.club_name.data
            club_profile.university = form.university.data
            club_profile.location = form.location.data
            club_profile.description = form.description.data
            club_profile.contact_person = form.contact_person.data
            club_profile.phone = form.phone.data
        else:
            # Create new profile
            club_profile = ClubProfile(
                user_id=current_user.id,
                club_name=form.club_name.data,
                university=form.university.data,
                location=form.location.data,
                description=form.description.data,
                contact_person=form.contact_person.data,
                phone=form.phone.data
            )
            db.session.add(club_profile)
        
        db.session.commit()
        flash('Club profile saved successfully!', 'success')
        return redirect(url_for('club_dashboard'))
    
    # Pre-populate form if editing
    if club_profile:
        form.club_name.data = club_profile.club_name
        form.university.data = club_profile.university
        form.location.data = club_profile.location
        form.description.data = club_profile.description
        form.contact_person.data = club_profile.contact_person
        form.phone.data = club_profile.phone
    
    return render_template('create_event.html', form=form, title='Club Profile')

@app.route('/sponsor/profile', methods=['GET', 'POST'])
@login_required
def create_sponsor_profile():
    """Create or edit sponsor profile"""
    if current_user.user_type != 'sponsor':
        flash('Access denied. Sponsors only.', 'error')
        return redirect(url_for('index'))
    
    form = SponsorProfileForm()
    sponsor_profile = current_user.sponsor_profile
    
    if form.validate_on_submit():
        if sponsor_profile:
            # Update existing profile
            sponsor_profile.company_name = form.company_name.data
            sponsor_profile.industry = form.industry.data
            sponsor_profile.location = form.location.data
            sponsor_profile.description = form.description.data
            sponsor_profile.website = form.website.data
            sponsor_profile.budget_range = form.budget_range.data
            sponsor_profile.target_demographics = form.target_demographics.data
            sponsor_profile.contact_person = form.contact_person.data
            sponsor_profile.phone = form.phone.data
        else:
            # Create new profile
            sponsor_profile = SponsorProfile(
                user_id=current_user.id,
                company_name=form.company_name.data,
                industry=form.industry.data,
                location=form.location.data,
                description=form.description.data,
                website=form.website.data,
                budget_range=form.budget_range.data,
                target_demographics=form.target_demographics.data,
                contact_person=form.contact_person.data,
                phone=form.phone.data
            )
            db.session.add(sponsor_profile)
        
        db.session.commit()
        flash('Sponsor profile saved successfully!', 'success')
        return redirect(url_for('sponsor_dashboard'))
    
    # Pre-populate form if editing
    if sponsor_profile:
        form.company_name.data = sponsor_profile.company_name
        form.industry.data = sponsor_profile.industry
        form.location.data = sponsor_profile.location
        form.description.data = sponsor_profile.description
        form.website.data = sponsor_profile.website
        form.budget_range.data = sponsor_profile.budget_range
        form.target_demographics.data = sponsor_profile.target_demographics
        form.contact_person.data = sponsor_profile.contact_person
        form.phone.data = sponsor_profile.phone
    
    return render_template('create_sponsor_profile.html', form=form, title='Sponsor Profile')

@app.route('/event/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create new event"""
    if current_user.user_type != 'club':
        flash('Access denied. Clubs only.', 'error')
        return redirect(url_for('index'))
    
    if not current_user.club_profile:
        flash('Please complete your club profile first.', 'warning')
        return redirect(url_for('create_club_profile'))
    
    form = EventForm()
    if form.validate_on_submit():
        event = Event(
            club_id=current_user.club_profile.id,
            name=form.name.data,
            description=form.description.data,
            theme=form.theme.data,
            event_date=form.event_date.data,
            location=form.location.data,
            expected_footfall=form.expected_footfall.data,
            target_audience=form.target_audience.data,
            sponsor_requirements=form.sponsor_requirements.data,
            monetary_requirement=form.monetary_requirement.data,
            material_requirement=form.material_requirement.data,
            marketing_requirement=form.marketing_requirement.data,
            past_engagement_stats=form.past_engagement_stats.data,
            tags=form.tags.data
        )
        
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully!', 'success')
        return redirect(url_for('club_dashboard'))
    
    return render_template('create_event.html', form=form, title='Create Event')

@app.route('/event/<int:event_id>')
@login_required
def event_details(event_id):
    """View event details"""
    event = Event.query.get_or_404(event_id)
    
    # Get AI recommendations if current user is a sponsor
    recommendations = []
    if current_user.user_type == 'sponsor' and current_user.sponsor_profile:
        score = ai_matcher.calculate_match_score(event, current_user.sponsor_profile)
        explanations = ai_matcher.get_match_explanation(event, current_user.sponsor_profile)
        recommendations = {
            'score': score,
            'percentage': int(score * 100),
            'explanations': explanations
        }
    
    return render_template('event_details.html', event=event, recommendations=recommendations)

@app.route('/sponsor/<int:sponsor_id>')
@login_required
def sponsor_details(sponsor_id):
    """View sponsor details"""
    sponsor = SponsorProfile.query.get_or_404(sponsor_id)
    return render_template('sponsor_details.html', sponsor=sponsor)

@app.route('/search/events', methods=['GET', 'POST'])
@login_required
def search_events():
    """Search events (for sponsors)"""
    if current_user.user_type != 'sponsor':
        flash('Access denied. Sponsors only.', 'error')
        return redirect(url_for('index'))
    
    form = SearchForm()
    events = []
    
    if form.validate_on_submit():
        query = Event.query
        
        if form.keyword.data:
            keyword = f"%{form.keyword.data}%"
            query = query.filter(
                Event.name.ilike(keyword) |
                Event.description.ilike(keyword) |
                Event.theme.ilike(keyword) |
                Event.tags.ilike(keyword)
            )
        
        if form.location.data:
            location = f"%{form.location.data}%"
            query = query.filter(Event.location.ilike(location))
        
        if form.theme.data:
            theme = f"%{form.theme.data}%"
            query = query.filter(Event.theme.ilike(theme))
        
        if form.min_footfall.data:
            query = query.filter(Event.expected_footfall >= form.min_footfall.data)
        
        events = query.order_by(Event.created_at.desc()).all()
        
        # Add match scores if sponsor has profile
        if current_user.sponsor_profile:
            events_with_scores = []
            for event in events:
                score = ai_matcher.calculate_match_score(event, current_user.sponsor_profile)
                events_with_scores.append({
                    'event': event,
                    'score': score,
                    'percentage': int(score * 100)
                })
            events = sorted(events_with_scores, key=lambda x: x['score'], reverse=True)
    
    return render_template('search_events.html', form=form, events=events)

@app.route('/messages')
@login_required
def messages():
    """View messages"""
    sent_messages = Message.query.filter_by(sender_id=current_user.id).order_by(Message.created_at.desc()).all()
    received_messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.created_at.desc()).all()
    
    return render_template('messages.html', sent_messages=sent_messages, received_messages=received_messages)

@app.route('/message/send/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id):
    """Send message to user"""
    recipient = User.query.get_or_404(recipient_id)
    form = MessageForm()
    
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            subject=form.subject.data,
            content=form.content.data
        )
        
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
        return redirect(url_for('messages'))
    
    return render_template('messages.html', form=form, recipient=recipient)

@app.route('/message/mark_read/<int:message_id>')
@login_required
def mark_message_read(message_id):
    """Mark message as read"""
    message = Message.query.get_or_404(message_id)
    if message.recipient_id == current_user.id:
        message.read = True
        db.session.commit()
    
    return redirect(url_for('messages'))

@app.route('/interest/express/<int:event_id>')
@login_required
def express_interest(event_id):
    """Express interest in an event (for sponsors)"""
    if current_user.user_type != 'sponsor':
        flash('Access denied. Sponsors only.', 'error')
        return redirect(url_for('index'))
    
    if not current_user.sponsor_profile:
        flash('Please complete your sponsor profile first.', 'warning')
        return redirect(url_for('create_sponsor_profile'))
    
    event = Event.query.get_or_404(event_id)
    
    # Check if interest already exists
    existing_interest = SponsorInterest.query.filter_by(
        sponsor_id=current_user.sponsor_profile.id,
        event_id=event_id
    ).first()
    
    if existing_interest:
        flash('You have already expressed interest in this event.', 'info')
    else:
        interest = SponsorInterest(
            sponsor_id=current_user.sponsor_profile.id,
            event_id=event_id,
            interest_level='medium'
        )
        
        db.session.add(interest)
        db.session.commit()
        flash('Interest expressed successfully!', 'success')
    
    return redirect(url_for('event_details', event_id=event_id))

@app.route('/sponsors')
def sponsors_showcase():
    """Public page showing sample sponsors with their requirements"""
    # Get sample sponsors from the database or create sample data
    sponsors = SponsorProfile.query.limit(10).all()
    
    # If no sponsors in database, create sample data for display
    if not sponsors:
        sponsors = [
            {
                'company_name': 'TechCorp Innovation',
                'industry': 'Technology',
                'location': 'San Francisco, CA',
                'description': 'Leading technology company specializing in AI and machine learning solutions. We support student innovation and tech entrepreneurship.',
                'website': 'https://techcorp.example.com',
                'budget_range': '$10,000 - $50,000',
                'target_demographics': 'Computer Science students, Engineering students, Tech enthusiasts',
                'contact_person': 'Sarah Johnson',
                'phone': '+1 (555) 123-4567',
                'sponsorship_interests': ['Tech Hackathons', 'AI/ML Workshops', 'Career Fairs', 'Innovation Competitions']
            },
            {
                'company_name': 'Green Future Energy',
                'industry': 'Renewable Energy',
                'location': 'Austin, TX',
                'description': 'Sustainable energy company committed to environmental education and green technology advancement.',
                'website': 'https://greenfuture.example.com',
                'budget_range': '$5,000 - $25,000',
                'target_demographics': 'Environmental Science students, Engineering students, Sustainability advocates',
                'contact_person': 'Michael Chen',
                'phone': '+1 (555) 234-5678',
                'sponsorship_interests': ['Environmental Fairs', 'Clean Tech Competitions', 'Sustainability Workshops', 'Green Innovation Events']
            },
            {
                'company_name': 'FinanceFirst Solutions',
                'industry': 'Financial Services',
                'location': 'New York, NY',
                'description': 'Premier financial services firm offering banking, investment, and fintech solutions. We invest in future financial leaders.',
                'website': 'https://financefirst.example.com',
                'budget_range': '$15,000 - $75,000',
                'target_demographics': 'Business students, Economics majors, Finance enthusiasts',
                'contact_person': 'Emily Rodriguez',
                'phone': '+1 (555) 345-6789',
                'sponsorship_interests': ['Business Plan Competitions', 'Finance Workshops', 'Entrepreneurship Events', 'Career Networking']
            },
            {
                'company_name': 'HealthTech Innovations',
                'industry': 'Healthcare Technology',
                'location': 'Boston, MA',
                'description': 'Healthcare technology company developing cutting-edge medical devices and digital health solutions.',
                'website': 'https://healthtech.example.com',
                'budget_range': '$8,000 - $40,000',
                'target_demographics': 'Pre-med students, Biomedical Engineering students, Health Science majors',
                'contact_person': 'Dr. James Park',
                'phone': '+1 (555) 456-7890',
                'sponsorship_interests': ['Medical Innovation Fairs', 'Health Tech Hackathons', 'Research Symposiums', 'Medical Device Competitions']
            },
            {
                'company_name': 'EduConnect Learning',
                'industry': 'Education Technology',
                'location': 'Seattle, WA',
                'description': 'Educational technology platform transforming online learning experiences for students worldwide.',
                'website': 'https://educonnect.example.com',
                'budget_range': '$3,000 - $20,000',
                'target_demographics': 'Education majors, Computer Science students, Learning enthusiasts',
                'contact_person': 'Lisa Thompson',
                'phone': '+1 (555) 567-8901',
                'sponsorship_interests': ['EdTech Competitions', 'Learning Innovation Workshops', 'Student Teaching Events', 'Educational Research Conferences']
            },
            {
                'company_name': 'SportsTech Dynamics',
                'industry': 'Sports Technology',
                'location': 'Denver, CO',
                'description': 'Sports technology company creating innovative solutions for athlete performance and fan engagement.',
                'website': 'https://sportstech.example.com',
                'budget_range': '$5,000 - $30,000',
                'target_demographics': 'Sports Management students, Athletic teams, Fitness enthusiasts',
                'contact_person': 'Ryan Martinez',
                'phone': '+1 (555) 678-9012',
                'sponsorship_interests': ['Sports Innovation Competitions', 'Athletic Events', 'Fitness Challenges', 'Sports Analytics Workshops']
            }
        ]
    else:
        # Convert database objects to dict format for consistent template handling
        sponsors = [{
            'company_name': s.company_name,
            'industry': s.industry,
            'location': s.location,
            'description': s.description,
            'website': s.website,
            'budget_range': s.budget_range,
            'target_demographics': s.target_demographics,
            'contact_person': s.contact_person,
            'phone': s.phone,
            'sponsorship_interests': ['Custom sponsorship opportunities based on your needs']
        } for s in sponsors]
    
    return render_template('sponsors_showcase.html', sponsors=sponsors)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
