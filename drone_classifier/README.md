This is a drone classifier trained on 1000 positive images and 1000 negative images. 

The script is from: https://github.com/MCGallaspy/cascade-trainer

The cascade works okay but another refiner method should be added to make the system more robust 
alteratively train on larger set of example images (see the repository for how to train a haar-cascade object detector).

To run the code on a image:

```bash
>> python detect.py test_set/index.jpg
```

Or for a directory:

```bash
>> python detect.py -r test_set
```