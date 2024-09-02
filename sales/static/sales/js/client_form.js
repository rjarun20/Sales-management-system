$(document).ready(function() {
    $('.selectpicker').selectpicker();

    // Hardcoded list of states and cities for India
    var statesAndCities = {
        "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Tirupati", "Rajahmundry"],
        "Arunachal Pradesh": ["Itanagar", "Tawang", "Pasighat"],
        "Assam": ["Guwahati", "Dibrugarh", "Jorhat", "Silchar", "Tezpur"],
        "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Purnia"],
        "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg"],
        "Goa": ["Panaji", "Margao", "Vasco da Gama", "Mapusa", "Ponda"],
        "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Jamnagar"],
        "Haryana": ["Gurgaon", "Faridabad", "Panipat", "Ambala", "Hisar"],
        "Himachal Pradesh": ["Shimla", "Manali", "Dharamshala", "Mandi", "Solan"],
        "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Hazaribagh"],
        "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru", "Hubli", "Belagavi"],
        "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Thrissur", "Kannur"],
        "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain"],
        "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad", "Thane"],
        "Manipur": ["Imphal", "Churachandpur", "Thoubal"],
        "Meghalaya": ["Shillong", "Tura", "Jowai"],
        "Mizoram": ["Aizawl", "Lunglei", "Champhai"],
        "Nagaland": ["Kohima", "Dimapur", "Mokokchung"],
        "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Puri", "Sambalpur"],
        "Punjab": ["Chandigarh", "Ludhiana", "Amritsar", "Jalandhar", "Patiala"],
        "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
        "Sikkim": ["Gangtok", "Namchi"],
        "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli"],
        "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar"],
        "Tripura": ["Agartala", "Udaipur"],
        "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Allahabad", "Ghaziabad"],
        "Uttarakhand": ["Dehradun", "Haridwar", "Rishikesh", "Haldwani"],
        "West Bengal": ["Kolkata", "Howrah", "Darjeeling", "Asansol", "Siliguri", "Durgapur"]
    };
    

    // Set India as the default and only option
    var countrySelect = $('#country');
    countrySelect.empty();
    countrySelect.append('<option value="India" selected>India</option>');
    countrySelect.selectpicker('refresh');
    countrySelect.prop('disabled', true);

    // Populate the state dropdown
    var stateSelect = $('#state');
    stateSelect.empty();
    stateSelect.append('<option value="">Select State</option>');
    $.each(statesAndCities, function(state, cities) {
        stateSelect.append('<option value="' + state + '">' + state + '</option>');
    });
    stateSelect.selectpicker('refresh');

    // Populate the city dropdown based on the selected state
    $('#state').on('change', function() {
        var state = $(this).val();
        var citySelect = $('#city');
        citySelect.empty();
        citySelect.append('<option value="">Select City</option>');
        if (state && statesAndCities[state]) {
            $.each(statesAndCities[state], function(index, city) {
                citySelect.append('<option value="' + city + '">' + city + '</option>');
            });
        }
        citySelect.selectpicker('refresh');
    });

    // Set initial values if editing a client
    if (initialState) {
        $('#state').val(initialState).selectpicker('refresh').trigger('change');
        if (initialCity) {
            setTimeout(function() {
                $('#city').val(initialCity).selectpicker('refresh');
            }, 100);
        }
    }

    // Add custom state and city if not in the list
    $('#state, #city').on('changed.bs.select', function (e, clickedIndex, isSelected, previousValue) {
        var select = $(this);
        if (select.val() === null) {
            var newValue = prompt("Please enter the " + (select.attr('id') === 'state' ? "State" : "City") + " name:");
            if (newValue) {
                select.append(new Option(newValue, newValue, true, true)).selectpicker('refresh');
            }
        }
    });
});
