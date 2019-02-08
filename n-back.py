# import libraries
import os, sys, pygame, random, text_wrapper, inputbox, csv

# initialize
pygame.init()
pygame.mixer.quit()

# create clock object and frame limiter
clock=pygame.time.Clock()
maxfps = 60

# create window
window = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
center = window.get_rect().center
pygame.mouse.set_visible(False)

# collect subject information
while True:
    condition = int(inputbox.ask(window, 'Condition'))
    if condition == 1 or condition == 2:
        break

subject = str(inputbox.ask(window, 'Sub Num'))
sona_id = int(inputbox.ask(window, 'SONA ID'))
subject_age = str(inputbox.ask(window, 'Age'))
subject_sex = str(inputbox.ask(window, 'Sex'))

# set default Font
fontName = pygame.font.match_font('Times New Roman')
font = pygame.font.Font(fontName, 28)

# set some colours
grey = (128,128,128)
black = (0,0,0)
white = (255,255,255)
red = (200,0,0)
green = (0,200,0)
blue = (0,0,200)
pink = (255,192,203)
background_colour = black
stim_colour = white

# set allowed keys
escapeKey = pygame.K_ESCAPE
endKey = pygame.K_e
toggleKey = pygame.K_t
continueKey = pygame.K_RETURN
responseKey = pygame.K_SPACE
yesTargetKey = pygame.K_l
noTargetKey = pygame.K_a
screenshotKey = pygame.K_p

# display messages
text_pos = (100,100)
wrapSize = (1200,1200)
text_spacing = 1

# wait screen message
waitScreen = text_wrapper.drawText("Waiting for the researcher...",
    stim_colour, surface=pygame.transform.scale(window, wrapSize), lineSpacing = text_spacing, font=font)

# instruction sets
p1_instruct = text_wrapper.drawText("In this experiment you will be performing an attention task called a 2-back. For this task, you will be presented with letters, one at a time, in the center of the screen. Your task is to press the SPACEBAR when the CURRENT letter matches the letter presented two letters back."
    +"\n\nFor example, you might see the sequence:"
    +"\nF-B-X-B-K-M-H"
    +"\n\nIn the above example, a correct response pattern would be:"
    +"\npress nothing (F) - press nothing (B) - press nothing (X) - press the spacebar (B) - press nothing (K) - press nothing (M) - press nothing (H)"
    +"\n\nPlease do your best to perform this task to the best of your ability.",
    stim_colour, surface=pygame.transform.scale(window, wrapSize), lineSpacing = text_spacing, font=font)

p2_instruct = text_wrapper.drawText("We are now going to complete a few practice trials to help you become familiar with the task."
    +"\n\nAny questions before we begin?",
    stim_colour, surface=pygame.transform.scale(window, wrapSize), lineSpacing = text_spacing, font=font)

p1_instruct_list = [p1_instruct[0],p2_instruct[0]]

# practice over message
pracOver = text_wrapper.drawText("The practice trials are now over. Any questions?",
    stim_colour, surface=pygame.transform.scale(window, wrapSize), lineSpacing = text_spacing, font=font)

# end of experiment message
taskOver = text_wrapper.drawText("Please notify the researcher that you have finished.",
stim_colour, surface=pygame.transform.scale(window, wrapSize), lineSpacing = text_spacing, font=font)

# define stimuli
my_letters = ("B","F","K","H","M","Q","R","X","Z")
num_trials = 468
num_practice = 18

# function to create n-back trial list
def generateTrials(num_iterations):
    nback = 2
    temp_stim_list = [None]*num_iterations
    temp_targ_list = [0]*num_iterations
    i = 0
    j = 0
    ticks = 0
    #for all trials
    while i < num_iterations:
        #get a stimulus
        item_index = random.randint(0,len(my_letters)-1)
        the_stim = my_letters[item_index]
        j+=1
        #add first few
        if i<nback:
            temp_stim_list[i] = the_stim
            i+=1
        #control for unmarked targets, check nback
        elif (i == nback or i == nback+1) and the_stim !=temp_stim_list[i-nback]:
            temp_stim_list[i] = the_stim
            i+=1
        #control for unmarked targets, check nback and nback*2
        elif i > nback+1 and the_stim !=temp_stim_list[i-nback] and the_stim!=temp_stim_list[i-nback*2]:
            temp_stim_list[i] = the_stim
            i+=1
    #NOTE: the conjoined rules are:
    #1) that stimuli cannot match n-back and n-back*2 (above)
    #2) targets cannot be +/- n-back of each other (below)
    
    #set target frequency
    target_frequency = .1667
    num_targets = int(num_iterations*target_frequency) #78 targets, 390 non-targets
    i = 0
    j = 0
    targets_added = 0
    used_index_list = []
    #get a random target position
    while i < num_targets:
        target_index = random.randint(nback,num_iterations-1)
        j+=1
        #if hasn't been used yet, use it
        if not (set([target_index,target_index-nback,target_index+nback]) & set(used_index_list)):
            #record target positions
            temp_targ_list[target_index] = 1
            used_index_list.append(target_index)
            i+=1
            targets_added+=1
    #for all trials, switch in target stimuli
    for i in range(num_iterations):
        #if trial is target and nback trial was not target
        if(temp_targ_list[i] == 1 and temp_targ_list[i-nback]!=1):
            #make trial stimulus the same as nback
            temp_stim_list[i] = temp_stim_list[i-nback]
        #elif trial is target and nback trial is also target (double jump)
        elif(temp_targ_list[i] == 1 and temp_targ_list[i-nback] == 1):
            #make trial stimulus the same as nback*2
            temp_stim_list[i] = temp_stim_list[i-nback*2]
            #make nback stimulus the same as nback
            temp_stim_list[i-nback] = temp_stim_list[i-nback*2]
    return temp_stim_list,temp_targ_list

# trial information
stim_duration = 500 #
mask_duration = 2000 #2
trial_duration = stim_duration+mask_duration
#468 trials, 2500 total, 19.5 minutes

# data holders
data = []

# pre-render some text
get_ready_msg = pygame.font.Font(fontName,28).render("Get Ready...", True, stim_colour, background_colour)
get_ready_msg_rect = get_ready_msg.get_rect()
get_ready_msg_rect.center = center

# a function to draw our stimuli in center of screen
def drawStim(stimulus):
    font = pygame.font.Font(fontName,100)
    stim = font.render(stimulus, True, stim_colour, background_colour)
    stim_rect = stim.get_rect()
    stim_rect.center = center
    window.blit(stim,stim_rect)
    return stim_rect

# a function to cover stimuli with rectangle of equal size
def coverStim(stim_rect):
    pygame.draw.rect(window,background_colour,stim_rect)

# a function to draw some text to screen
def drawScreen(text_to_draw):
    pygame.display.update([window.fill(background_colour), window.blit(text_to_draw,text_pos)])

# a generic response loop
def responseLoop():
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == escapeKey:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == continueKey:
                done = True
            elif event.type == pygame.KEYDOWN and event.key == screenshotKey:
                pygame.image.save(window, "screenshot_"+str(random.randint(1,999))+".png")
        clock.tick(maxfps)
    pygame.display.update(window.fill(background_colour))

# 'get ready...' message
def getReady():
    pygame.display.update(window.blit(get_ready_msg,get_ready_msg_rect))
    pygame.time.wait(stim_duration)

    coverStim(get_ready_msg_rect)
    fix_rect = drawStim("+")
    pygame.display.update()
    pygame.time.wait(mask_duration)

    pygame.display.update(coverStim(fix_rect))

# core experimental loop
def runTrial(recordData,stop,trial,the_stimList,the_targList):
    stimulus = the_stimList[trial]
    is_target = the_targList[trial]

    stim_rect = drawStim(stimulus)

    stimulus_at = pygame.time.get_ticks()
    end_at = stimulus_at + trial_duration

    fixation_on = False
    has_pressed = False
    RT = "NA"
    response = "NA"
    omission = 1

    if is_target == 1:
        hit = 0
        miss = 1
        false_alarm = "NA"
        correct_rejection = "NA"
    else:
        hit = "NA"
        miss = "NA"
        false_alarm = 0
        correct_rejection = 1

    while pygame.time.get_ticks() < end_at and not stop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                saveData()
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == endKey:
                stop = True
                break
            if event.type == pygame.KEYDOWN and event.key == responseKey and not has_pressed:
                RT = pygame.time.get_ticks() - stimulus_at
                has_pressed = True
                omission = 0
                response = "target"
                if is_target == 1:
                    hit = 1
                    miss = 0
                else:
                    false_alarm = 1
                    correct_rejection = 0

        if not fixation_on and pygame.time.get_ticks()-stimulus_at >= stim_duration:
            coverStim(stim_rect)
            drawStim("+")
            fixation_on = True

        pygame.display.update()
        clock.tick(maxfps)

    if recordData == True:
        data.append([subject, sona_id, subject_sex, subject_age, condition, trial, stimulus, is_target, omission, response, RT, hit, false_alarm, correct_rejection, miss])

    return stop

# function to save the data
def saveData():
    headers = ['subNum','sonaid','gender','age','condition','trial', 'stimulus','is_target','omission','response','RT','hits','false_alarms','correct_rejections','misses']
    with open ("data/"+str(subject)+ "_"+str(sona_id)+"_data.csv", "wb") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for i in data:
            writer.writerow(i)
        f.flush()
        f.close()

# --------------------------------------------------------------------
# ----------------------EXPERIMENT STARTS HERE------------------------
# --------------------------------------------------------------------

# generate practice trials
practiceStimList, practiceTargList = generateTrials(num_practice)

# generate experimental trials
stimList, targList = generateTrials(num_trials)

# display wait screen
drawScreen(waitScreen[0])
responseLoop()

# display instructions
for i in p1_instruct_list:
    drawScreen(i)
    responseLoop()

# do practice trials
recordData = False
getReady()
stop = False
for p in range(len(practiceStimList)):
    stop = runTrial(recordData, stop, p, practiceStimList, practiceTargList)
    if stop:
        break

# display practice over screen
drawScreen(pracOver[0])
responseLoop()

# do experimental trials
recordData = True
getReady()
stop = False
for t in range(len(stimList)):
    stop = runTrial(recordData,stop,t,stimList,targList)
    if stop:
        break

# display end screen message
drawScreen(taskOver[0])
done=False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            done = True
    clock.tick(maxfps)
saveData()
pygame.quit()
sys.exit()
