from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import platform
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.common.exceptions import NoSuchElementException
from json import dump, load
import sys
from os.path import exists

# to do later: change based on platform and default browser; configure chromedriver resiliency; build robust and dynamic options selection; add multiple page options

key_bindings = {'Remote' : ["filter-remotejob", "filter-remotejob-menu"], 'Date Posted' : ["filter-dateposted", "filter-dateposted-menu"], 'Salary Estimate' : ["filter-salary-estimate", "filter-salary-estimate-menu"], 'Job Type' : ["filter-jobtype", "filter-jobtype-menu"], 'Location' : ["filter-loc", "filter-loc-menu"], 'Experience Level' : ["filter-explvl", "filter-explvl-menu"], 'Radius' : ["filter-radius", "filter-radius-menu"], 'Company' : ["filter-cmp", "filter-cmp-menu"]}

def config_indeed():

    print("Please enter preferred search term: ")
    search_term = input()

    remote_options = ['Remote', 'Temporarily Remote', 'N/A']
    print("Remote Work Preferences: \n")
    for option in remote_options:
        print(option + "\n")
    print("Your Remote Preference Is: ")
    remote_pref = input()
    assert remote_pref in remote_options

    date_posted_options = ['24 hours', '3 days', '7 days', '14 days', 'N/A']
    print("Date Posted Options: \n")
    for option in date_posted_options:
        print(option + "\n")
    print("Your Date Posted Preference Is: ")
    date_posted_pref = input()
    assert date_posted_pref in date_posted_options

    salary_options = ['30,000+', '35,000+', '40,000+', '50,000+', '65,000+', 'N/A']
    print("Salary Options: \n")
    for option in salary_options:
        print(option + "\n")
    print("Your Salary Preference: ")
    salary_pref = input()
    assert salary_pref in salary_options

    job_options = ['Internship', 'Full-time', 'Part-time', 'Temporary', 'Contract', 'N/A']
    print("Job Type Options: \n")
    for option in job_options:
        print(option + "\n")
    print("Your Job Type Preference: ")
    job_pref = input()
    assert job_pref in job_options

    lvl_options = ['Entry', 'Mid', 'Senior', 'N/A']
    print("Experience Level Options: \n")
    for option in lvl_options:
        print(option + "\n")
    print("Your Experience Level Preference: ")
    lvl_pref = input()
    assert lvl_pref in lvl_options

    print("If you have a location preference, enter it here (please limit yourself to grammatically correct and appropriately short and general locations, i.e. 'New York' or 'Brooklyn' or 'Jericho'): ")
    loc_pref = input()

    indeed_prefs = {'search' : search_term, 'Remote' : remote_pref, 'Date Posted' : date_posted_pref, 'Salary Estimate' : salary_pref, 'Job Type' : job_pref, 'Experience Level' : lvl_pref, 'Location' : loc_pref, 'Education' : "filter-taxo1"}

    with open("indeed_prefs.json", "a") as f:
        dump(indeed_prefs, f)
    return

def indeed_start():

    options = Options()
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(executable_path="./chromedriver", options=options)
    driver.get("http://www.indeed.com")
    #assert "Indeed" in driver.title
    return driver

def save_indeed_jobs(driver):
    jobs = driver.find_elements_by_xpath("//div[@class='job_seen_beacon']")
    job_list = {}
    for j in range(len(jobs)):
        title = jobs[j].find_element_by_class_name("jobTitle.jobTitle-color-purple").text
        companyName = jobs[j].find_element_by_class_name("companyName").text
        salary = ""
        try:
            salary = jobs[j].find_element_by_class_name("estimated-salary").text
        except NoSuchElementException:
            pass
        description = jobs[j].find_element_by_class_name("job-snippet").text
        jdict = {'title' : title, 'companyName' : companyName, 'salary' : salary, 'description' : description}
        job_list[j] = jdict
    with open("indeed_jobs.txt", "a") as f:
        for i in range(j):
            f.write(job_list[i].get('companyName') + " : " + job_list[i].get('title') + "\n")
            if (job_list[i].get('salary') != ""):
                f.write(job_list[i].get('salary') + "\n")
            else:
                f.write("No estimated salary\n")
            f.write(job_list[i].get('description') + "\n\n")
    # run a sep prog that chooses which to run and closes driver at end
    driver.close()
    driver.quit()

def get_indeed_preset():

    if not exists("indeed_prefs.json"):
        print("No json file to use")
        exit()

    data = {}
    with open("indeed_prefs.json", "r") as f:
        data = load(f)

    driver = indeed_start()
    elem = driver.find_element_by_name("q")
    elem.clear()
    elem.send_keys(data.get('search'))
    elem.send_keys(Keys.RETURN)

    sleep(1)
    filter_count = 0
    for key in data: # add trying for disappearing categories
        if key == 'search':
            continue
        if data.get(key) != 'N/A':
            driver.find_element_by_id(key_bindings.get(key)[0]).click()
            try:
                driver.find_element_by_partial_link_text(data.get(key)).click()
            except NoSuchElementException:
                print("Could Not Filter By " + key + "\n")
                filter_count -= 1
                pass
            filter_count += 1
        sleep(1)
        if filter_count == 1:
            driver.find_element_by_class_name("popover-x-button-close.icl-CloseButton").click()
            sleep(1)

    save_indeed_jobs(driver)
#print(job_list[0].get('title'))
#assert "No results found." not in driver.page_source

def indeed_no_config(): # write code to launch and return driver?

    driver = indeed_start()
    elem = driver.find_element_by_name("q")
    elem.clear()
    print("What would you like to search for on Indeed: ")
    search = input()
    elem.send_keys(search)
    elem.send_keys(Keys.RETURN)
    sleep(1)

    filter_counter = 0

    while True:
        print("Would you like to filter the search results, 'y' / 'n': ")
        y = input()
        if y == 'y':
            categories = driver.find_elements_by_class_name("yosegi-FilterPill-dropdownPillContainer")
            print("Which of the following categories would you like to filter by (please enter name exactly as printed)?")
            for category in categories:
                if category.text != "within 25 miles":
                    print(category.text)
            category = input()
            #assert category in categories
            driver.find_element_by_id(key_bindings.get(category)[0]).click()
            options = driver.find_elements_by_id(key_bindings.get(category)[1])
            print("Which of the following options would you prefer to select (feel free to use unique snippets)?")
            for option in options:
                print(option.text)
            option = input()
            try:
                driver.find_element_by_partial_link_text(option).click()
            except NoSuchElementException:
                print("Failed to filter")
                filter_counter -= 1
                pass
            filter_counter += 1
            sleep(1)
            if filter_counter == 1:
                driver.find_element_by_class_name("popover-x-button-close.icl-CloseButton").click()
                sleep(1)
        else:
            break

def main():
    n = len(sys.argv)
    if n != 2:
        print("Program takes 2 arguments; Options:")
        print("python3 indeed.py -c: Configure json file to autorun searches on indeed")
        print("python3 -a: Run autosearch using json file")
        print("python -r: Run search with inputs")
    if sys.argv[1] == "-c":
        config_indeed()
    elif sys.argv[1] == "-a":
        get_indeed_preset()
    elif sys.argv[1] == "-r":
        indeed_no_config()
    else:
        print("Program takes 2 arguments; Options:")
        print("python3 indeed.py -c: Configure json file to autorun searches on indeed")
        print("python3 -a: Run autosearch using json file; if no json file, exits")
        print("python3 -r: Run search with inputs")

if __name__ == "__main__":
    main()
    


