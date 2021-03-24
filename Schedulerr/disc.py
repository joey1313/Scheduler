import discord
import asyncio
import time
from datetime import datetime
from datetime import timedelta

'''
    Write a task in the following format~:
    task_name | duration
'''
def add_task(list):
    f = open("info.txt", "a")
    list_text = " | ".join(list) + "\n"
    f.write(list_text)
    f.close()

'''
    Read tasks
    Creates a list of lists of task_name | duration
'''
def read_task():
    f = open("info.txt", "r")
    meow = [line.rstrip('\n') for line in f]
    task_list = [x.split(' | ') for x in meow]
    f.close()
    return task_list

def read_raw_task():
    f = open("info.txt", "r")
    task_list = f.read()
    f.close()
    return task_list

'''
    Reads settings
    character | study duration | break duration
'''
def read_settings():
  f = open("settings.txt", "r")
  setting_list = f.read().split(' | ')
  f.close()
  return setting_list

'''
    Writes settings list to settings.txt
'''
def write_settings(list):
  f = open("settings.txt", "w")
  setting_text = " | ".join(list)
  f.write(setting_text)
  f.close()

'''
    Read study times
    subject | total_time | sessions
'''
def read_study_time():
  f = open("study_time.txt", "r")
  meow = [line.rstrip('\n') for line in f]
  study_times = [x.split(' | ') for x in meow]
  f.close
  return study_times

def read_raw_study_time():
  f = open("study_time.txt", "r")
  raw_study_times = f.read()
  f.close
  return raw_study_times
'''
    !!!
'''
def write_study_time(subject, time):
  previous = read_study_time()
  f = open("study_time.txt", "w")
  new = []
  exists = False
  for subjects, times, sessions in previous:
    if subject == subjects:
      new.append(" | ".join([subject, str(int(times) + time), str(int(sessions) + 1)]))
      exists = True
    else:
      new.append(" | ".join([subjects, times, sessions]))
  if exists == False:
    new.append(" | ".join([subject, str(time), str(1)]))
  list_text = "\n".join(new)
  f.write(list_text)
  f.close()

'''
    reads intermissions.txt
'''
def read_intermissions():
  f = open("intermissions.txt", "r")
  intermissions_list = f.read().split(' | ')
  f.close()
  return intermissions_list

'''
    writes to intermissions.txt
'''
def write_intermissions(list):
  f = open("intermissions.txt", "w")
  intermissions_text = " | ".join(list)
  f.write(intermissions_text)
  f.close()

class MyClient(discord.Client):
    '''
        init function
    '''
    def __init__(self):
      init_list = read_settings()
      self.ch = init_list[0]
      self.study_time = int(init_list[1])
      self.break_time = int(init_list[2])
      self.broken = False
      self.paused = False
      super().__init__()

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_message(self, message):
      def check_msg(m):
        if m.channel == message.channel and m.author == message.author:
          return True
        # we do not want the bot to reply to itself
      def RepresentsInt(s):
          try:
              int(s)
              return True
          except ValueError:
              return False
      def check_int(m):
        if check_msg(m):
          if RepresentsInt(m.content):
            return True

      if message.author.id == self.user.id:
          return

      # set default study session settings
      if message.content == (self.ch + 'settings'):


        settings = read_settings()
        text = "Bot prefix: {}\nStudy Time: {}\nBreak Time: {}".format(settings[0],settings[1],settings[2])

        await message.channel.send('Current settings:\n{}'.format(text))
        await message.channel.send('Do you want to change the bot prefix? (Recommended no)')
        answer = await client.wait_for('message', check=check_msg)

        # sets bot prefix command
        if answer.content.lower() == 'yes' or answer.content.lower() == 'y':
          await message.channel.send('What do you want the bot symbol to be?')
          answer = await client.wait_for('message', check=check_msg)
          prefix = answer.content
          await message.channel.send('Bot Prefix will be set to {}'.format(prefix))

        else:
          prefix = settings[0]

        # sets default study and break times
        await message.channel.send('What do you want the study time to be?')
        answer = await client.wait_for('message', check=check_int)
        study_time = answer.content

        await message.channel.send('Study Time will be set to {}'.format(study_time))
        await message.channel.send('What do you want the break time to be?')
        answer = await client.wait_for('message', check=check_int)
        break_time = answer.content

        await message.channel.send('Break Time will be set to {}'.format(break_time))
        setting_list = [prefix, study_time, break_time]
        write_settings(setting_list)

        await message.channel.send('Settings have been set!')

      # adds homework session to list of tasks
      if message.content == (self.ch + 'schedule'):
        await message.channel.send('What is your subject?')
        answer = await client.wait_for('message', check=check_msg)
        subject = answer.content
        await message.channel.send('What is your duration (in minutes)?')
        answer = await client.wait_for('message', check=check_int)
        duration = answer.content
        list = [subject, duration]
        add_task(list)
        await message.channel.send('Scheduled {0} for {1} minutes'.format(subject, duration))

      '''
        1. Get the durations
        2. Split them into 30 minute intervals
        3. If the previous duration is shorter than 30
        3a. if the current duration is longer than 30 - prev duration, subtract that amount from duration & add the subject
        3b. if the current duration is shorter than 30 - prev, add subject & duration onto the list and pop subject & duration
        4. if previoud duration is greater or equal to 30, do the same thing as if it was a new list
        Make a new 2D list with task(s), duration
      '''

      def schedulize(task_list):
        if len(task_list) == 0:
          print("ur bad")
          return
        subject, duration = [x for x, y in task_list],[int(y) for x, y in task_list]
        new_list = []
        while len(duration) > 0:
          if len(new_list) == 0:
            if duration[0] <= self.study_time:
              new_list.append([subject[0],duration[0]])
              subject.pop(0)
              duration.pop(0)
            else:
              new_list.append([subject[0],self.study_time])
              duration[0] -= self.study_time
          else:
            if new_list[-1][1] < self.study_time:
              if new_list[-1][1] + duration[0] > self.study_time:
                new_list[-1][0] += (" & {}".format(subject[0]))
                duration[0] -= self.study_time - new_list[-1][1]
                new_list[-1][1] = self.study_time
              else:
                new_list[-1][0] += (" & {}".format(subject[0]))
                new_list[-1][1] += duration[0]
                subject.pop(0)
                duration.pop(0)
            else:
              if duration[0] <= self.study_time:
                new_list.append([subject[0],duration[0]])
                subject.pop(0)
                duration.pop(0)
              else:
                new_list.append([subject[0],self.study_time])
                duration[0] -= self.study_time
        new_list_with_breaks = []
        for i in new_list:
          new_list_with_breaks.append(i)
          new_list_with_breaks.append(["Break", self.break_time])
        new_list_with_breaks.pop(-1)
        return new_list_with_breaks

      # prints out a schedule of all the homeworks and breaks
      def print_schedule(task_list):
        subject_list = []
        duration_list = []
        #intermissions_list = read_intermissions()

        for task in task_list:
          subject, duration = task
          subject_list.append(subject)
          duration_list.append(duration)

        now = datetime.now() - timedelta(hours=4)
        current_time = now.strftime('%H:%M:%S')
        final_string = ""

        for i in range(len(task_list)):
          new_time = (now + timedelta(minutes=int(duration_list[i]))).strftime('%H:%M:%S')

          '''for intermission in intermissions_list:
            #if now before event_time and new_time after event_time
            intermission_time = now.replace(hour=int(intermission[1]), minute=int(intermission[2]))
            intermission_time = type(intermission)
            print(intermission_time)'''

          final_string += '{0} -- {1} to {2}\n'.format(subject_list[i], current_time, new_time)
          current_time = new_time
          now = now + timedelta(minutes=int(duration_list[i]))

        return final_string

      # calls print_schedule function
      if message.content == (self.ch + 'print_schedule'):
        await message.channel.send(print_schedule(schedulize(read_task())))

      # calles intermission function (not finished) to add non-homework tasks/events
      if message.content == (self.ch + 'intermission'):
        await message.channel.send('What is the name of your event?')
        answer = await client.wait_for('message', check=check_msg)
        event_name = answer.content

        await message.channel.send('What is the hour of {0}?'.format(event_name))
        answer = await client.wait_for('message', check=check_msg)
        event_hour = answer.content

        await message.channel.send('What is the minute of {0}?'.format(event_name))
        answer = await client.wait_for('message', check=check_msg)
        event_minute = answer.content

        await message.channel.send('How long is {0}?'.format(event_name))
        answer = await client.wait_for('message', check=check_msg)
        event_length = answer.content

        intermissions_list = [event_name, event_hour, event_minute, event_length]
        write_intermissions(intermissions_list)



      # start enacting schedule
      if message.content == (self.ch + 'start_HW'):
          ts = 0

          # check if paused
          def check_PAUSED(m):
            if check_msg(m):

              # resume session
              if m.content == (self.ch + 'resume_HW'):
                return True

          def check_HW(m):
            if check_msg(m):

              # end session
              if m.content == (self.ch + 'finish_HW'):
                self.broken = True
                return True

              # pause session
              if m.content == (self.ch + 'pause_HW'):
                self.broken = True
                self.paused = True
                return True

          #Wait for time to be over
          #When time is over, start break
          #When break is over, start the next homework if there is one.
          #If there is no more homework, say "Finished!"
          task_list = read_task()
          new_task_list = schedulize(task_list)

          '''
            Given: task_list
            task_list
          '''
          await message.channel.send(print_schedule(new_task_list))
          for (i, task) in enumerate(new_task_list):
              subject, duration = task
              ts = datetime.now().timestamp()

              if subject == 'Break':
                await message.channel.send("Time for a break {0.author.mention}! Take a {1} minute break!".format(message, self.break_time))

              else:
                await message.channel.send("{0.author.mention}! Start working on {1}!".format(message, subject))

              try:
                  await client.wait_for('message', check=check_HW, timeout=int(duration))
                  print('meow')

              except asyncio.TimeoutError:
                  print("timed out")

              print('{}{}'.format(self.broken,self.paused))

              if self.broken:
                  time_studied = datetime.now().timestamp() - ts
                  if subject != "Break":
                    write_study_time(subject, ts)
                  self.broken = False

                  if self.paused:
                    remainder = duration - time_studied

                    print("remainder: {}".format(remainder))

                    new_task_list.insert(i+1,[subject, remainder])
                    await message.channel.send("PAUSED; type {}resume_HW to continue.".format(self.ch))
                    await client.wait_for('message', check=check_PAUSED)
              else:
                write_study_time(subject, duration)

              # take break / end break
              if self.paused:
                await message.channel.send("Resuming Homework!")
                self.paused = False

              elif subject == 'Break':
                await message.channel.send("Hope you're feeling refreshed, {0.author.mention}! Let's get back to work!".format(message))

              else:
                await message.channel.send("{0.author.mention}! Good job on {1}!".format(message, subject))

          await message.channel.send("Homework Finished!")

      if message.content == (self.ch + 'schedulize'):
        await message.channel.send(schedulize(read_task()))

      if message.content == (self.ch + 'study_list'):
        await message.channel.send(read_raw_task())

      if message.content == (self.ch + 'read'):
        text = read_task()
        await message.channel.send(text)

      if message.content == (self.ch + 'study_times'):
        study_times = read_raw_study_time()
        await message.channel.send(study_times)

      if message.content == (self.ch + 'clear_study_times'):
        f = open("study_time.txt","w")
        f.write("")
        f.close()
        await message.channel.send("Study Times Cleared!")

      if message.content == (self.ch + 'average_study_times'):
        study_times = read_study_time()
        for i in study_times:
          subject, time, sessions = i
          await message.channel.send("{} | Average {}".format(subject, float(time) / int(sessions)))

      # clear list of tasks
      if message.content == (self.ch + 'clear_list'):
        f = open("info.txt", "w")
        f.write("")
        f.close()
        await message.channel.send("List Cleared!")

      # instructions for use
      if (self.ch + 'help') in message.content:
        await message.channel.send('''
        Here are all my functions:

        *{0}settings* - set default study and break times
        *{0}hello* - get a greeting

        *{0}schedule* - add a task to your list
        *{0}print_schedule* - see your schedule for today
        *{0}study_list* - See your current list of tasks
        *{0}clear_list* - clear the list of tasks
        *{0}study_times* - view accumulated study statistics
        *{0}clear_study_times* - clear accumulated study statistics

        *{0}start_HW* - start enacting your schedule
        *{0}pause_HW* - pause your study session
        *{0}resume_HW* - continue study session
        *{0}finish_HW* - end study session

        ***{0}annoy_leroy*** **- annoy Leroy**

        *{0}stop* - exit the program
        *{0}intermission* - set non-homework events (meals, activities, etc.)
        *{0}help* - see this list of commands
        '''.format(self.ch))

      # greetings
      if message.content == (self.ch + 'hello'):
          if message.author.id == 206035591027097601:
              await message.channel.send('meow')

          else:
              await message.channel.send('Hello {0.author.mention}'.format(message))

      # spam Leroy with smiley faces
      if message.content == (self.ch + 'annoy_leroy'):
          leroy = [x for x in message.guild.members if x.id == 342820764858187778][0]
          #await message.channel.send('{0.mention}'.format(leroy))
          await leroy.send('(͡° ͜ʖ ͡°) ') #hmmmmmmmmmmmmm

      # exit program
      if message.content == (self.ch + 'stop'):
          await message.channel.send('Goodbye!')
          await client.logout()

client = MyClient()
client.run('InsertKeyHere')