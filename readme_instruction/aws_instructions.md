Hey, hey, hey. Dup. Okay. Hello. Hi everyone. A very warm welcome to today's session on 
building prototypes on AWS. Uh first of all happy to everyone who is celebrating and thank 
you so much for joining us today so close to a huge festival and so first we'll start with um 
what are the submission requirements what is the uh updated deadline and then we'll see 
what AWS services to use and a few use cases followed by a live demo on how to how to 
build um prototypes using ko this is the agenda for today and before we deep dive into the 
technicalities I want to start with A massive congratulations to every single one of you. Um 
out of the thousands of developers who submitted their ideas for this hackathon, you are 
the elite few who have been shortlisted to move into the prototype development phase. Um 
your ideas really stood out in front of the jury members for their innovation um their 
potential to solve field challenges. So you should already be incredibly proud of yourselves 
because um we uh we clearly are. By reaching this stage, you are now one step closer to all 
the rewards and benefits that are associated with this program. And as a reminder, you are 
now competing for a share of 40 lakhs of prize pool along with certificates and most 
importantly getting your solutions in front of the top industry leaders at AWS. Okay. Now to 
make sure um everything that you have been working on it is correctly evaluated we need to 
be very clear about the submission process and there are four mandatory deliverables that 
every team must submit. First of all every team must submit only one solution as for the 
problem statement they have selected and most probably the team lead can do that or if 
you want any other team member to do that that is also possible. Everyone have the access 
to the same dashboard. You just need to navigate to the submission section. Um the very 
f
irst thing that you need to submit is a working prototype link. We need to see what you 
have built in action. So make sure that your hosted URL is live and accessible. Second is a 
demo video which should include a clear and concise explanation of the core functionalities 
and basically um the why behind your solution in under 30 minutes to not make the video 
too long. And wherever uh you post the video maybe you can share a link of um unlisted 
video on YouTube or a Google drive link or any um platform that you are selecting make sure 
that we all have the access and it is set on public basically. Third is a presentation deck that 
explains your problem statement your technical architecture and your solutions USP. Again 
while submitting make sure that you convert it into a PDF first and then upload it on the 
platform otherwise you might see some errors if you're trying to upload it in some other 
format. And last is your code your GitHub repository again it should be um hosted in a public 
repository so that we all have access to and we will be looking to your documentation and 
how you have utilized um several as services like Amazon Bedrock and more. Okay. Um 
please make sure that you remember all the key dates at this point of time. You just need to 
remember one date which is 8th of March with which is the extended deadline for 
prototype submissions. There will be no more extensions granted beyond this. So please 
make sure that you use this time wisely and you make uh you submit your prototypes before 
8th of March. So that's all that I have to share. Now um I would like to invite an she's field 
developer marketing manager at AWS for taking this session forward. Hi, thanks Shaa really 
to be here. Um firstly I'm an I lead the field developer marketing for AWS India. Uh basically 
what I primarily do is spend time with developers, figure out what's confusing, what's 
missing for them and try to make AWS a little less uh intimidating. So that's the energy we 
are coming in with today. And before I get into anything, I just want to acknowledge and 
congratulate each one of you that making it to phase two uh out of how however many 
teams that submitted is genuinely hard. A lot of people had ideas and you did something 
great with it. So that matters. Uh I just wanted to quickly u get a sense of the room. How 
many of you have actually deployed your solution or how many of you are just in the like you 
know the idea phase um I I'm reading the comments let me know in the chat how many of 
you have already deployed and how many of you are planning to deploy in the next few days 
meanwhile you do that I will get started with what you're here for to help you guide through 
what you're going to build in the uh building phase and what are the services you need to 
use and what are the things that we will be looking out for so we before we talk about 
anything specific I just want to set some context on how do we think about this phase there 
are four things that we believe genuinely will determine uh whether a submission does well 
and I want to be transparent about it because I think it will make you uh make better 
decisions with whatever time you have uh left. So first thing ideally we expect you to deploy 
it on AWS. AWS is the provides the biggest cloud infrastructure for to for you to take your 
prototype into production with all of the security uh scalability reliability in short. uh one of 
your submission requirements is also a working prototype URL right and the judging rubric 
also cares about what is your architecture quality and the AWS deployment so ideally I 
would suggest include AWS services in your stack uh don't leave points on the table and we 
will going ahead talk about what a minimal but credible AWS stack looks like uh so that 
that's going to help you second thing We want to focus on depth over breath. I know I know 
I've been a developer and participated hackathons. It's tempting to build everything uh 
especially when you have like a great idea and you have like what's four five days remaining. 
But what I've often seen is the teams that tend to do well um just pick the core user journey 
make it work end to end and make it work reliably. Reliability is the key word here. uh five 
halffinish features is harder to judge than one beautifully polished flow. Third, and this is a 
big one in my opinion, uh your AI needs to be doing real work. Uh there's a simple test for 
this. Imagine if you remove the AI layer from your app entirely, does it still function? Does it 
become slightly worse version of the same thing? If the answer is yes, then probably your AI 
is decorative. So judges have seen a lot of demos. They can tell the difference when the AI 
that's loadbearing and the AI that's been bolted on for appearances. Fourth is cost efficiency. 
We all live in the real world. So we will be looking at how thoughtful you are about your 
resources. Um I'll give you an example like you can catch the LLM responses and then 
choose the right compute for the job. not burning through the credits on calls you don't 
need to uh we'll go through some concrete ways to go about uh this as we go through the 
services okay services uh let me give you a little bit of a framing before we uh deep dive into 
that we will talk about primarily compute storage database the bare essentials of uh taking 
any prototype to production Let's start with um there are a lot of AWS services that we can 
recommend you uh for the kind of workloads you're building serverless AI first designed to 
scale and um if you don't have a DevOps team you can still continue deploying on uh AWS. 
So these are services that are either free or um free for the hackathon at least like within the 
credits that uh you can cover. On the flip side, there is no rule that you have to use exactly 
these services and nothing else. But definitely we would reward you for sticking to it. Um if 
services are like AWS services are completely act absent from your stack uh you will struggle 
a little bit on the implementation and the technical depth. So let's start with the most basics 
basic ones. U Lambda it's a event-driven um serverless way to deploy um get get access to 
compute and deploy our applications. EC2 if you want to uh if you need an always running 
server and uh one cool use case about AC EC2 is also that you can run your open source 
models if you're facing some throttling issues or something uh just use EC2 under your free 
t
ier use uh deploy an open source model and then you have full control over the 
environment and ECS Fargate allows you to uh use your dockerized apps you don't need to 
manage a server and then you and scale it as you go. Uh, next thing is storage. Storage is one 
of those things where I have seen people either overthink it or don't think about it at all until 
uh something breaks. Uh, S3 basic, everybody knows about it. 5 GB free. It's an object based 
storage. And the mental model, uh, it's it's it's pretty simple. Anything that isn't a structured 
database lives in S3. You upload your files, document um your AI is going to process and the 
outputs that your model is going to generate audio files, images, all of that goes into S3. And 
I know since you've made it to the prototype uh development phase, you know what a 
storage is used for. And uh half of um world's most important websites I've seen have S3 
something in their link. So it's very commonly used. And um one one more thing that a lot of 
people don't realize is you can you host your entire front end on S3. Like if your React or 
NextJS app is currently in versel or you can build it and push the output to an S3 bucket with 
static hosting enabled and just put a CloudFront in front of it. Uh we can talk about 
cloudfront later but that's how you deploy an AWS front end. It's like uh less than an hour of 
work. I personally did it and it meaningfully changes your architecture story. Instead of just 
click and deploy, you're using reliability, scalability and security in your architecture. Second 
is EFS which is an elastic file system. It's the other storage option, but it's more specific. Like 
this is the place you would reach for it if you're running a lambda function that needs to 
share a persistent file system between invocations or uh one of the most common use cases 
is rag. Uh if your lambda needs to read from a set of files that persists across calls, EFS is 
cleaner than trying to work around uh S3 for that. Also 5 GB free. So practically speaking 
almost everybody would need an S3 uh subset of team building rack pipelines will need uh 
EFS also and neither will cost you for the limited scale we are currently operating at. Third 
one is databases. I'll start with Dynamob. It's uh your could be your default database for this 
hackathon. Not because I am insuring it or enforcing but uh I've looked at some solution. It 
sort of fits better than the other alternatives too. Uh it's 25GB free. Uh not for 12 months 
but always free for 25 GBs. It's serverless. There's no cluster to configure and no connection 
pooling to think about. You just define a table. You start reading and writing. Uh that's it. It 
handles the session state, chat history, user records, job cues, health data, whatever your 
app is tracking and it scales automatically as well. Um, also something to think about uh 
because it also directly affects your cost efficiency. You can also cache your bedrock 
responses in Dynamob. Um, simple hash your input, check Dynamob first. If it's if there's a 
hit, return the cache response. If not then you call bedrock and store the result. I've seen uh 
this in one of the submissions uh if you're in the chat uh glad to uh see that like it it was a 
genuine nice way of saving cost then there is RDS if you genuinely need a relational data 
with complex joins but I don't think it's there in most of the solutions but if you're using it 
that's a great option for you. Um and then finally open search is for vector search primarily. 
If you're building a rag and need a semantic uh retrieval beyond bedrock knowledge basis uh 
this trial tier is available. Uh but I'd start with bedrock knowledge basis and only reach for 
open search if you like have a specific limitation for your uh data. What about bedrock 
knowledge basis? Uh we'll cover that in the geni slide. Right. So, bedrock is the platform that 
t
ies all of your geni together. Uh, it is manages your access to foundational models and no 
infrastructure is needed. Uh, Nova light usually suffices for most tasks and Nova Pro when 
you need heavier reasoning reasoning. Um, I know a lot of you have been facing some issues 
with bedrock specifically. Uh, and we have addressed those and we hear you. We also have 
um a special guest later in the call who will tell you more about how to like you know sort of 
f
igure out your throttling limitations and uh what are the best ways to use uh bedrock. So we 
recommend but using bedrock but if you're facing um issues that you are unable to work 
around or we are not able to help you uh you're open to call model this directly using APIs. 
Um and then let me talk more about the other uh genai suite of services bedrock knowledge 
basis. It handles your rack pipelines end to end like you just upload your documents and it 
takes care of chunking, embedding, storing uh and retrieval. So um you don't write any of 
that u mechanism yourself. If if your app answers the questions from a document corpus, 
this is your fastest path and some problem statements do require you to do that. Um 
bedrock agent core. This is the latest production grade way to build agentic AI applications 
on AWS. It's G now and you can build, deploy and operate agents at any scale uh using any 
framework which is why I personally prefer it. Lang graph, crewi, lama index and any model 
without having to manage the infrastructure. So you don't have to um if you're building an 
agenti application, if you're building agents for your use cases, I know some people are um 
the most relevant parts within uh bedrock agent core would be agent core runtime uh agent 
core memory and agent core gateway. So runtime is a serverless environment with session 
isolation. um supports longunning agents memory uh manages your long-term memory and 
session context. Uh agent core gateway allows you to connect to tools and APIs with 
minimum uh connection. And one more thing about agent core that I want to highlight is for 
this hackathon, it works with any open-source framework and any foundation model. So you 
don't have to rewrite what you've already built. Um if you've got a langraph agent running 
locally right now uh agent core runtime is how you get it deployed with proper session 
isolation and observability without spending a lot of time your infrastructure. Uh yeah so I 
know uh AP south one u the region when you select for bedrock you have been facing some 
issues switch to US east one it's the default and absolute last resort you can also use on EC2 
uh but please try um retry logic with exponential um back off on every model call like don't 
let a single throttle bring your uh demo down. Quick one. Uh this is what you've already 
used in your uh idea submission phase. Uh it's pretty it's your AI agent AI coding assistant 
and we've seen how you've um it's showing up in the repos and how you're using 
requirement MD and design. MD files. So it's a natural next step for you to be able to um 
want to build like the requirements and the design. MD files what you're building in plain 
language and then KO can read it generate an architecture breakdown and then break it into 
tasks and then uh scaffolds the boiler plate lambda handlers Dynamob table schemas I roll 
configs it generates all of that from your spec. So the easiest way to deploy on AWS when 
you already have requirements MD and design MD is to continue using KO. So I'm just just 
suggesting how how you can save time. I'm going to spend just quick five minutes to talk 
about some cool projects that I've already seen. Um like I went through all of the entries and 
these are some examples where you've used AWS in some ways or not used AWS at all and 
just want to give an example of how do we look at it. So the AI code anal an analyzer is using 
the essential stack lambda, dynamob, bedrock and this this is the solution that uh has an 
interesting caching pattern. They hash every code input before calling bedrock. Check 
Dynamo DB first and only hit the model if it's a new input. The second time someone 
submits the code snippet, they get a response in millisecond at zero model cost. It's a simple 
idea, but what a beautiful implementation. I was really proud of whoever did that. And then 
AI health companion, uh, it has a multi- aent architecture. Uh, supervisor agent coordinating 
f
ive specialized agents. Uh, Dynamob stores the patient history across sessions and S3 tracks 
how things change over time. versioning in S3. And what's interesting is that these agents 
have distinct and nonover overlapping jobs. Each one does its own thing. So that's what 
takes a multi- aent architecture credible to judges. Not that it has five agents, but each agent 
has a reason to exist. We are not impressed by complexity, the usability of those. U 
somebody built an interview platform. Uh it's a great uh way of seeing how you pick the 
right tools. So they're using bedrock for evaluating answers and uh reasoning quality 
relevance and all those and then uh an external speech to text because um it was they have 
mentioned also a clear description uh that why did did they choose uh a third party speech 
to text because the audio handling they felt it was more accurate there. So two AI providers 
each doing what it's best at the and the app is already live. Uh last one is the bug 
reproduction uh agent. It has a swappable LLM provider wide envir environment variables by 
default but you can switch to other parties as well. Um on the demo day if one of the model 
has issues they switch to another one. So this is what I was talking about that it it has to be 
resilient it has to be reliable. So you have thought about failure mode as well which is 
something that we look out for. One last thing is just want to give you a quick overview of 
how do we look at scoring. Um implementation is 50%. Half your score comes from whether 
your app actually works or not. Uh judges will navigate to your live URL without you having 
to hold their hand. they'll click around if it breaks, if it's slow to the point of frustration or if 
it shows a local host address, half the marks are gone there. So, focus on the 
implementation part. Prioritize this above everything else. Technical depth is where the 
quality of your architecture shows up. What we mentioned in the previous slides, did you 
make any deliberate choices? Is your error handling solid? Can you explain why you use 
Dynamo DV over RDS? I would suggest you doing that but and why you chose lambda over 
EC2 or ECS and your readme matters here and so does your ability to answer questions 
clearly on demo day. Cost efficiency 10% um I personally like like this one the most because 
with it's easier to keep scaling your solution without thinking about the real world 
implementation of it. uh I gave you an example how they were uh using Dynamob caching 
patterns and similar ways you can always use to be cost efficient and then impact and 
business viability are 10% each is this solution solving a problem for the real people of India 
uh can it be an actual product can uh can you describe who is the target audience if if there's 
a user group which is a concrete problem you score well here quickly uh letting you know of 
the common mistakes that I've seen and worst one is always that it's not deployed on the 
demo day. It happens more than you guys think. Uh teams spend all of their time building 
and then leave deployment to the last day. Something goes wrong and they end up demoing 
a local host app or a recorded video. So fix is simple. Deploy early even if it's incomplete, 
even if half the features don't work. uh and then you can keep iterating on it so that you 
know what's breaking. Um second one is not having a fallback. Um if your entire app 
depends on single bedrock call and the call throttles in demo day, your demo is over. So it 
maybe takes one or two hours to wire in some other uh LLM as a fallback. So please do it. 
And the third is the AI is just a wrapper. Uh so I've seen a lot of demos where the entire AI 
layer is just a system prompt on top of a foundational model with no domain specific logic, 
no grounding in real data or no behavior that's specific to the use case. So uh just make it 
interesting and I have seen a lot of solutions which are not this. So I'm really glad at the 
current state of submissions and the phenomenal work you guys have done. Uh the baseline 
is a live URL that works. Anything uh AI that's doing a meaningful domain specific work your 
services deployed on AWS at least two services bare minimum and the ability to explain the 
architectural decisions that you have uh made. That's pretty much it. I know you might have 
a lot of questions and want to see things hands-on. For that uh we have our friend who will 
continue taking this. So that's what I'd leave with. Uh build something you're genuinely 
proud of. Um and uh now I would like to uh invite Prau who is a solutions architect at AWS to 
take you through the next bit of the session. >> A hunch thank you. Am I audible? >> Yes pu 
you're audible. Um so yeah good evening good afternoon everyone. So like an uh talked 
about what is the expected level of the prototype has to be and how it has to be you know 
accessible through a link what all the minimum service expected to be there things like that. 
So I have a demo to show. So I'll first show the demo the working demo and if you can build 
something equivalent of it um that would be fair enough. So I'll share my screen. Okay 
before going there. Yeah. So I built a demo called AI learning assistant like what you can see 
in the screen. So very lightweight application where I have a static uh front end hosted in my 
S3 website. And then it's fronted by cloudfront which is our content delivery network. Then 
from there we have an API gateway that goes and call lambda function. Lambda function is 
where I've written all the logic to perform for that AI learning assistant. And um for model 
access I have went with Nova 2 light which got released in this last reinvent December 2025. 
um it goes to bedrock gets the answer and gives it back to the user and it also saves a 
conversation in the S3 bucket. Okay, so let me quickly share my screen to show the demo. 
Okay. So this is the link. As you can see it is in CloudFront. I open it. I paste it again. It still 
works right. So it's a live demo link and basically then my prompt is you know it's like a 
learning assistant. Keep your answer clear and concise and whatever I ask it will just answer 
me. So for example there are some predefined question let me ask how does DNS work I 
click. So the AP call goes to the lambda and lambda hits a bedrock and bedrock I have no to 
light that you know gives you this answer. So I go back and even if I ask something like Even 
if I ask you to explain a piece of code for example I write explain and enter it takes some 
t
ime but it will perform the job. So explanation of Fibonacci function and whatn not. So 
whenever you prepare a demo, ensure that it is up to this mark where anyone can use it and 
uh test it out. Whatever your use case it should be able to test that functionality. That's how 
the demo has to be. Okay. So like again we have discussed the architecture. Now I'll show 
you something. I hope my ko screen is visible. Okay. Not sure how many of you have started 
using Ko. Okay. I'll reure. Okay. So this is KO and uh basically like I have built and deployed 
the application which I have shown using KO. Okay. But there are some it's not as part of the 
AF for Barackathon. This is something that comes from me. Um so there are different 
approach that you can take to build a prototype. Right? So these days you have entire AI 
assistant with you and you can do build deploy test what not you can do everything with 
that. So I share some of the approach. Okay. approach one what you can do is you can use 
KO for brainstorming and you write the code all by yourself and then go to the AWS console 
either deploy it that way or create a you know cloud for template or a CDK cloud distribution 
kit deployment anything of your wish to deploy whatever you have written. Okay. So here 
you are using a platform a tool this AI tool like Kirro for brainstorming and you write the 
code and then you deploy. Then then second approach let the AI assistant like Ko to write 
the code and then you go and deploy. Third assistant third approach let KO to do both the 
work. Write the code deploy the code test it and then you just have that demo link to access 
and see if everything looks good. But as you all are you know students and professionals if 
you have never tested never been hands on with AWS platform or any any anything that is 
close close to you know building your own application. I would recommend not to go with 
an approach where you are leveraging the any AI assistant like Kirro or anything for that 
matter to let it completely write and to let it completely deploy. Okay, why I'm saying so 
because you'll never get the chance to learn things by yourself. You'll never know what is the 
error that you're going to encounter and how we going to resolve it and all of it. Talking 
about the era that we were living before that AI. So these are the approach you pick what 
works best for you but use ko to you know brainstorming and to even write code but do not 
use ko to entirely write code and do the deployment as well. So that would be my 
recommendation from an engineer standpoint. Okay. So now coming back to this. So I have 
my use case you know clearly sorted um like here. So based on whatever uh an I've 
presented. So like you see I have uh my compute running on lambda function um storage I'm 
using an S3 to host my static file and also my conversational logs for AI element I'm using 
bedrock I mean I'm using Nova 2 like model and then API is API gateway. Okay. So I have 
created this prompt already. So what I can do I just copy paste. I'm not sure how many 
people have seen this. There is also another YouTube video that you can see where we talk 
about how you can use ko. But there are two modes wi and spec mode. But when you are 
building anything from the scratch you can go with the spec mode. Spec mode is a 
specificationdriven development where what you see on the left side is a specification. I 
want this on this way. This is what I'm trying to achieve. I'm giving my specification with the 
specification as a input. Kira will draft the plan. It will design the it will sh state the 
requirement then the design technical design and then the task to accomplish that. Okay. So 
if I just paste this prompt and enter it will take a while and then it will realize that it this 
should be a spec driven thing and it will start designing the requirement and all three files. 
Okay. So it says that if you can see this looks like a solid project a web- based AI learning 
assistant using Lambda S3 bucket blah blah. It's a new feature, right? There is also a new 
feature in um Ko that you can also use spec to you know for bug fix which is when you 
already have an application brownfield use case where you want to fix any bug in that case 
also you can use the spec mode but for us we are building something from the scratch what 
we call as green field and I click on build a feature and submit answer and what happens is is 
to start designing the requirement requirement is nothing but user story. So a user who 
wants to you know present at a front end web page and then there is a chatbot chat box 
where he can interact. All of this thing we'll get into as a user stories that you would see in a 
minute. I am reading the questions. I will get back to some of the common questions post 
this demo. So until then like uh So it looked at the workspace it sees nothing because the 
green field project I have no resource anything related to this project. So it will start creating 
the requirement. You can just click on the requirement. It will take a few seconds you know 
for it to load. And uh regarding the ko if you sign up you will get as a free tire as a 50 credits 
but if you're signing for the first time you do get a 500 credit as a bonus credit for the very 
f
irst time. So 550 500 credits would be fair enough to build a demo project. Okay. So for 
every user extensive user it might not be applicable but if you ask experiment in right way 
you not necessarily or most likely will not consume that 500 for one specific demo. So this is 
how the requirement will looks like and uh and yeah this is just an idea you don't really have 
to do this way. We are not just uh guiding you that this is how you should do. We're just 
showing you one possibility that you can leverage Kirome to build your application. Then if 
I'm okay with my requirement, I generally go to the next option where I'll ask it to generate a 
design for it. Okay. So these are the user stories. Now in order to you know achieve this, 
what should be my technical design? What what should be my tech stack should look like? 
So then it will start creating the designs for it. For now it will be empty but soon you will 
start to see the design as well. So in the interest of time what I do I just go and show you the 
one which I've already created. Okay. I hope the screen is visible. An can you confirm if you 
can? Okay. Okay. This visible. Okay. So the same prompt which I have used earlier and uh this 
is these are the requirements and uh this is the design for it. Basically you can see the 
mermaid diagram representation user from the user browser click on the static website 
hosted in the S3 through the cloudfront they hit that index.html HTML then as soon as they 
type their question that API is triggered / ask through that API gateway it's a rest API it it's a 
lambda lambda function it has its own logic it will invoke the bitrock model which is a noa to 
light gets the answer saves a conversation in the s3 lock and uh it also shows the task that is 
required to complete this so I have got about you six task with all the unit testing, property 
based testing, everything. I ran all the task and what happens here you will get that entire 
repo built and now you can deploy. for deployment. I have my AWS credential uh embedded 
like there is an extension that you can use uh as AWS uh you can get it in the extension and 
there you load your credential and from there you just guide which region and which 
account it has to be deployed and you can also deploy it through the terminal. The terminal 
you'll get it from here. If you top right if you click you'll get the terminal and uh if you have 
seen I have done a SAM build serverless application and then I deployed it and then I got the 
output stack as well. This is my cloudfront and if I click it it will take you take take it to the 
learning assistant page. Okay. So now I'll show you the resources from the AWS console 
point in Okay, I hope my cloud formation stack is visible and um I ran it I think somewhere 
last night and uh you can see the events the resources it created the cloud friend CloudFront 
distribution link the lambda and even that uh S3 bucket. If I go to the S3 bucket, this is where 
my index.html will be there right and uh what not. So this is my bedrock and see if you have 
created the new account they have recently retired that model access page earlier. If you 
want to access a model, you have to go to model access page specifically click on the model 
and say like I need to enable this and then you will start using it. But now you can just access 
the model and for most of prototypes that you are building you not necessarily need like re 
like models like clot. I know there are some concerns you need to have a different set of 
processes to follow it. But all I did used was you know Nova light. So if you go to the model 
catalog in 2025 December 4 months back we have launched this model called Nova 2 light. 
You can see 2nd of December 2025 and even this is very costefficient model and you can 
check the pricing of it later. It's extremely cost efficient compared to claude and even other 
other models in the market. Okay. And all you have to use is this model ID when you are 
invoking it. And for Nova if you are using it there is something called inference profile that 
you have to use which is already predefined something called US Amazon Nova 2 light and 
then you can basically hit the model with this inference profile and you will get the response 
back. So even if I have to go to my lambda function. So I have it mentioned as Amazon 2 
Nova light tool Nova to light and it works my system prompt and all of it. So try 
experimenting with the lightweight models in most use cases it should work and if not you 
always have one or the other way to you know to justify let's say like said you can have your 
own Olama in EC2 and there are lot of open-source model these days very lightweight like 4 
billion and 2 billion version some there are the yesterday they have released a quen version 
in 0.8 8 billion that can run in your mobile as well. Okay. So, so what we are looking at is how 
of you have designed whether the AI element that you have is it really necessary to have it 
whether it it performs a meaningful task there for any reason if bedrock is not failing to work 
as an engineer you can always figure out and way like there are plenty of other option that 
you can do right what we recommend just try this it should work in most scenarios If not, 
experiment with other backup options, alternative options. And last but not the least, if you 
are worried about the cost, um, just open cost explorer. Ignore my account billing, but scroll 
down. And then you will see something like budgets. In the budget just set up whatever the 
budget you are you have and then you will get the alarm triggered. So for this month I have 
went and I'm 82%age of my budget which is 164. So anytime when I hit 200 eventually I will 
get an alarm. So this is my previous year, previous month uh track record. So anyway, so 
there are plenty of options for it and um that would be it. Um so try and do let us know. In 
the meantime, let me go through the questions and see if I can answer one or two. Uh, and 
I'm I'm done. So, yeah. Okay. So, yeah, this throttle exception, right? I don't know how many 
of you all seen something like this. retry with back off pattern. Okay. So not just for the 
bedrock any AWS services it could be any any any cloud provider or any services right let's 
say you you host a function you host a service there is a limit that you cannot handle beyond 
that particular limit or a capacity. So um when you try to hit with a multiple number of 
requests within um given period of time you often it throttle exceeded error message. It 
generally happens when you send a burst of request within a period of time for example 10 
request in 1 second or 100 request in 1 second. So that's where in while building an 
application they will consider this uh best practices retry with backoff pattern which means 
whenever there is an error it will retry and then it slowly you know raise that number of 
request ensure like it is not exceeding that uh throttling limit. So try to follow that as well 
and also when you design the application see how much of request like it generally sends to 
the bedrock or whatever the model is. For example, let's say you submit a question or to an 
agent that you are building and you have a multiple agent in the back end and each of them 
have their own logic to perform and all those people sending a 10 to 20 request in a in a less 
than a second of time. Yes, there is a chance that you will get that throttle error. So 
whenever you see an error, go back and identify. You can go to the cloud trial and see how 
much of requests that you have sent and how you can control it. So, so, so how I integrated 
uh and deployed. So, Ko you can have an extension that extension you can have your AWS 
uh profiles your AM credentials directly configured and then I will call that in my with my Ko 
I just say like use this profile and for the deployment deploy the stack and then it'll deploy 
but I can also deploy from here as long as my terminal knows which is my AWS environment 
which uh region I'm looking at you can do it. So for example um there are commands in uh 
AWS like you can just say see AWS configure list it shows my account and access key and 
whatn not so you can configure your own account in your terminal that way you can access 
but we don't recommend it there is other alternative called AWS space login. So you can 
login using your uh how you are access login through browser. That way you can login in the 
terminal as well. So your terminal now knows that this is my environment where I need to 
you know execute this. Then your terminal will directly work with your AWS account and 
whatever the context which is happening on the terminal KO will know. So that way you can 
do it. Okay. So many questions. KO that there is no AWS credit for KO they both are different 
uh different mechanism pricing mechanism but like I said if you sign up for the first time 
you'll get that 500 bonus and you can you can work on Hi prahu, thanks for taking the 
questions. >> I mean there are a lot guys. I'm like I'm just figuring out which one to answer. 
So yeah, sorry about it. I'm just looking at >> yeah let's just see the ones which are recurring 
and uh maybe we can um bedrock nova API kotaas are zero TPM RPM completely blocked 
um is that a new account issue like when you create new accounts you're initially not given 
quotas >> um They're talking about bedrock, right? So what uh I think it that shouldn't be an 
issue like uh when they're giving access to the model zero TPM. >> Yeah. Meanwhile, let me 
help you with >> Yeah. >> Uh sorry. Uh start trying with you know US East one as a primary 
region when you're working with model. So even in my case I worked with US West one and 
uh whomsoever like if you still see that you know you're getting a kota as zero despite when 
you move to US east west one do let us know um yeah >> right and I see one question that 
model access is denied due to uh invalid payment instrument a valid payment instrument 
must be provided. So on AWS marketplace there are some issues with uh using Indian credit 
and debit cards because the model providers like there is some RBI mandate around it. So 
uh there are two ways to pay u like by the invoice also you can select that payment method 
and try it if the credit card is not working. uh but yes there is there are some issues with the 
accessing 3P models using marketplace but uh you can directly use those 3P models via APIs 
as well in your solution as long as you're using Lambda for the compute API gateway for the 
endpoints and uh S3 for the storage just for the LLM specific task even if you want to use 3P 
APIs under a free tier limit of any model provider feel free to include it as a part of your 
architecture because we do hear you and we do see that you are facing some issues with 
using bedrock in terms of um TPM RPM kotaas or throttling which prau guided you on how 
to work around but if you're still facing we understand it's a time bound thing feel free to 
access 3P models directly as well we would not recommend we would prefer bedrock there 
would be higher scoring points but uh if it comes to shove uh we go with what we have 
Yeah. >> Yeah. I think we have last two minutes for one question. Um, let me just scroll 
through it. I think most of the questions were about the exact same thing. Um, >> validation 
exception. Yeah. Yeah. Yeah. If if there's like a super exceptional case of um the CLI app that 
you've built for Kubernetes, uh you can mail us directly about it and like you know for one or 
two of exceptions we can see but a working prototype is a mandate for all uh submissions. 
Yeah. So this was pretty much uh our overview on what are the AWS services you can use. 
This was just a few out of the 200 plus services that we have. So feel free to search about 
what your problem is and then AWS service next to it what maps to it what can help you and 
if it's covered by the credits of free tier and continue with your build. And u ideally the 
takeaway is we recommend that for the barebones storage database uh compute you use 
the AWS stack. If you're facing any issues we would be open to flexibility for the geni layer. 
Uh try implementing bedrock but uh if you're still facing issues you can continue with direct 
uh model using APIs as well. and uh mock interview. No, if your solution gets selected, we'll 
see you directly at the demo day. And uh if mock interview is something that excites you, 
build it. That aligns with problem statement number one, AI for developer productivity and 
learning. So as long as you're building and you're learning, um that's that's what we're 
looking out for. And uh thank you so much Prau uh for answering the questions as well. >> 
Thank you. Thank you. Yeah. 