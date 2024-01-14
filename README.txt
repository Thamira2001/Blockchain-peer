===========================================WELCOME TO MY README ==========================================================================================================================================================================

		-completed til concensus 
			* meaning was able to find the longest chain and all peers with the same chain and i print it 				out to text file called example.txt . Everytime you run my code it will printout the 	
			   value of decision made BY concensus to that same file
			* MY CONCENSUS FUNCTION IS FOUND in peer2.py above function join_network
			* how it basically works is I first send stat request my 3 peers that im tracking 
			* then sleep the process for sometime to allow stat replies once replie sarrive it handles it by adding a dictionary that keeps track of height, hash combos as key and value being the original host and port of the peer that sends it so dict looks something like  (height, hash):(host,port) also adds to another dict which has key as hash and value as height and once these stat replies are hadnled i will access these dictionaries inside my concensus function to calculate the longest chain and what other peers are synced with the chain of heightHash combo
			* peronsally i think i did a good job by using alot of hashtables to reduce time and make concensus really really fast  

		-once conensus is doNE sent get block requests to all my peers that is synced with that chosen chain 				* this takes along time create the chain for some reason so im not sure if it worked 
				proeprly 

		-gossiping and gossip relpies are handled properly 

		-stat and stat replies are handled properly 



		- to run the code on  http://silicon.cs.umanitoba.ca:8998/do 
			python3 peer2.py
		- SALDY DIDNT HAVE TIME TO ADD COMMAND LINE ARGS :(((((((

		-once code is run it will show all the info im printing on the console There is alot btw didnt have time to narrow done how much i print to the console hence why i reidirected some important info like concensus info to a text file 


		-have not slept for two days but this assignment was really awesome 
		- hopefuly i did enough ! ;)


===========================================THANK YOU======================================================================================================================================================================================
